import requests
import urllib3
from llama_index.core import VectorStoreIndex, Document, StorageContext, load_index_from_storage
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os

# غیرفعال کردن اخطارهای امنیتی SSL (چون IP مستقیم میزنی)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------
# 1. تنظیمات مدل
# ---------------------------------------------------------
Settings.llm = Ollama(model="qwen2:1.5b", request_timeout=120.0)
Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-large")

# ---------------------------------------------------------
# 2. تنظیمات API
# ---------------------------------------------------------
API_BASE_URL = "https://185.204.170.142/api/v1"
# توکن را اینجا قرار بده (اگر منقضی شده، باید جدید بگیری)
AUTH_TOKEN = "1735%7CCfDJ8AHj4VWfmz9DpMpNxts7109iJyV5YLZVw3PwbvKW5DKqAEgJJH9q%2FbrwZH5%2Bea87uMdj4LXj58uTZ7snP8YcRP36uezVDspGvzUhEQTQ5Du4icTip2mah0Cq4C86s%2Bpy31PAxl%2FpsRIJXlugy7EmHgSgq9sOgSW9YPr%2BB1Pf2gdT4umedbopK1a0%2F6YKPrBL2Q9%2BNM2XzeBSmFcgXEvsT5rP28t%2BUIC2veZU99lS2849"
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

def fetch_all_pages(endpoint, item_processor_func, batch_size=100):
    """
    این تابع به صورت خودکار تمام صفحات API را ورق می‌زند و دیتاها را می‌گیرد.
    """
    documents = []
    skip = 0
    total_fetched = 0
    
    print(f"📥 Start fetching from: {endpoint}...")
    
    while True:
        params = {
            "PagingDto.PageFilter.Size": batch_size,
            "PagingDto.PageFilter.Skip": skip,
            "PagingDto.PageFilter.ReturnTotalRecordsCount": "true"
        }
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/{endpoint}", 
                params=params, 
                headers=HEADERS, 
                verify=False, 
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"⚠️ Error {response.status_code} in {endpoint}")
                break
                
            data = response.json()
            # طبق مستندات، دیتا معمولا در data.list یا ساختار مشابه است
            # اینجا فرض را بر ساختار استاندارد data['data']['list'] می‌گذاریم
            # با توجه به خروجی سواگر، برخی خروجی‌ها مستقیم آرایه هستند یا داخل data
            
            items = []
            if "data" in data and isinstance(data["data"], dict) and "list" in data["data"]:
                items = data["data"]["list"]
            elif "data" in data and isinstance(data["data"], list):
                items = data["data"]
            
            if not items:
                break  # پایان دیتا
                
            for item in items:
                doc = item_processor_func(item)
                if doc:
                    documents.append(doc)
            
            fetched_count = len(items)
            total_fetched += fetched_count
            skip += fetched_count
            
            print(f"   -> Fetched {fetched_count} items (Total: {total_fetched})")
            
            if fetched_count < batch_size:
                break # صفحه آخر
                
        except Exception as e:
            print(f"❌ Exception fetching {endpoint}: {e}")
            break
            
    return documents

# --- توابع پردازش هر نوع دیتا ---

def process_blog(item):
    # تبدیل دیتای بلاگ به متن قابل فهم برای مدل
    title = item.get("title", "")
    summary = item.get("summary", "")
    # اگر متن کامل (Body) در لیست نیست، ممکن است نیاز باشد با ID دوباره درخواست بزنی
    # اما فعلا Title و Summary را ایندکس می‌کنیم
    text = f"Title: {title}\nSummary: {summary}"
    return Document(text=text, metadata={"type": "blog", "id": item.get("id")})

def process_school(item):
    name = item.get("name", "")
    if "gamatrain" in name.lower(): return None # حذف موارد تستی
    
    city = item.get("cityTitle", "")
    desc = item.get("description", "") or "No description"
    text = f"School Name: {name}\nCity: {city}\nDescription: {desc}"
    return Document(text=text, metadata={"type": "school", "id": item.get("id")})

def process_question(item):
    # فرض بر ساختار سوال در API
    q_text = item.get("questionText", "") or item.get("title", "")
    if not q_text: return None
    text = f"Question Sample: {q_text}"
    return Document(text=text, metadata={"type": "question", "id": item.get("id")})

def process_subject(item):
    title = item.get("title", "")
    text = f"Educational Subject: {title}"
    return Document(text=text, metadata={"type": "subject", "id": item.get("id")})

def build_index():
    all_docs = []
    
    # 1. دریافت بلاگ‌ها
    all_docs.extend(fetch_all_pages("blogs/posts", process_blog))
    
    # 2. دریافت مدارس
    all_docs.extend(fetch_all_pages("schools", process_school))
    
    # 3. دریافت سوالات (اگر نیاز داری مدل سوال حل کند)
    all_docs.extend(fetch_all_pages("questions", process_question))

    # 4. دریافت دروس
    all_docs.extend(fetch_all_pages("subjects", process_subject))

    if not all_docs:
        print("⚠️ No data fetched! Check your TOKEN or API Access.")
        return None

    print(f"🚀 Total Documents to Index: {len(all_docs)}")
    
    # ذخیره‌سازی ایندکس
    if not os.path.exists("./storage"):
        index = VectorStoreIndex.from_documents(all_docs)
        index.storage_context.persist()
    else:
        ctx = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(ctx)
        
    return index

def main():
    index = build_index()
    if not index: return
    
    query_engine = index.as_query_engine()
    
    print("\n✅ System Ready! Ask your question:")
    while True:
        q = input("> ")
        if q in ["exit", "quit"]: break
        print(query_engine.query(q))

if __name__ == "__main__":
    main()
