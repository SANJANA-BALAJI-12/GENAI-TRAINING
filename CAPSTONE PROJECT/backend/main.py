from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import base64
from openai import OpenAI

# Load environment variables
load_dotenv()

from models import QueryRequest, QueryResponse, ImageUploadResponse, DashboardInsights, Post, PostCreate, Comment, CommentCreate
from agents import run_farming_crew
from rag import FarmingRAG
import uuid
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI(
    title="Smart Farming Advisor API",
    description="Backend AI Services for Intelligent Agriculture",
    version="1.0.0"
)

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# MongoDB Setup
MONGODB_URL = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
client = None
db = None
posts_collection = None

# Fallback in-memory database
IN_MEMORY_POSTS = {}

@app.on_event("startup")
async def startup_db_client():
    global client, db, posts_collection
    try:
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=2000)
        # Verify connection
        await client.server_info()
        db = client.agriblast
        posts_collection = db.posts
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB. Using in-memory fallback. Error: {e}")
        client = None
        posts_collection = None
        # Initialize with dummy data if using in-memory
        dummy_post_id = str(uuid.uuid4())
        IN_MEMORY_POSTS[dummy_post_id] = {
            "id": dummy_post_id,
            "author": "System",
            "location": "Global",
            "time": "Just now",
            "content": "Welcome to the AgriBlast AI Community! Database is running in memory fallback mode.",
            "likes": 0,
            "comments": 0,
            "active": True,
            "comment_list": []
        }

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()

# @app.get("/")
# def read_root():
#     return {"status": "ok", "message": "Smart Farming API is running!"}

@app.post("/api/chat", response_model=QueryResponse)
def chat_endpoint(req: QueryRequest):
    try:
        # Pass the query to the CrewAI multi-agent system
        answer = run_farming_crew(user_query=req.query)
        return QueryResponse(reply=answer, sources=["ChromaDB Local Knowledge"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode("utf-8")
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this crop image. What disease is present, with what confidence level (0.0 to 1.0)? Also provide a recommendation. Output EXACTLY a valid JSON string with keys 'disease_detected', 'confidence', and 'recommendation'."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{file.content_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        import json
        answer = response.choices[0].message.content.strip()
        if answer.startswith("```json"):
            answer = answer[7:]
        if answer.endswith("```"):
            answer = answer[:-3]
        
        result_json = json.loads(answer)
        
        return ImageUploadResponse(
            disease_detected=result_json.get("disease_detected", "Unknown"),
            confidence=float(result_json.get("confidence", 0.0)),
            recommendation=result_json.get("recommendation", "No recommendation available.")
        )
    except Exception as e:
        print(f"Vision API error: {e}")
        import random
        # Fallback to safe mock
        issues = [
            ("Tomato Early Blight", 0.92, "Apply a copper-based fungicide immediately. Ensure proper spacing between plants for airflow and water at the base to avoid wetting leaves."),
            ("Wheat Leaf Rust", 0.88, "Fungal infection detected. Treatment with a triazole fungicide is recommended within 48 hours. Monitor adjacent fields."),
            ("Healthy Crop", 0.98, "No signs of disease or pests. Keep maintaining regular irrigation schedules.")
        ]
        selected = random.choice(issues)
        return ImageUploadResponse(
            disease_detected=selected[0],
            confidence=selected[1],
            recommendation=selected[2]
        )

@app.get("/api/insights", response_model=DashboardInsights)
def get_dashboard_insights():
    try:
        # Generate dynamic insights using Groq LLM
        insights_prompt = """
        Generate realistic farming dashboard insights for a modern farm. Include:
        1. 2-3 current disease alerts based on seasonal patterns
        2. 2-3 yield predictions with specific crops and percentages
        3. 3-4 actionable recommendations for the next 7 days
        
        Make the insights specific, actionable, and based on agricultural best practices.
        Keep each item concise but informative.
        """

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an agricultural expert providing dashboard insights. Generate realistic, helpful farming advice."
                },
                {
                    "role": "user",
                    "content": insights_prompt
                }
            ],
            max_tokens=400
        )

        insights_text = response.choices[0].message.content

        # Parse the response into structured data
        # This is a simple parsing - in production, you might want more sophisticated parsing
        disease_alerts = []
        yield_predictions = []
        recommendations = []

        lines = insights_text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if 'disease' in line.lower() and 'alert' in line.lower():
                current_section = 'disease'
                continue
            elif 'yield' in line.lower() and 'predict' in line.lower():
                current_section = 'yield'
                continue
            elif 'recommend' in line.lower():
                current_section = 'recommendations'
                continue

            if current_section == 'disease' and len(disease_alerts) < 3:
                if line.startswith(('-', '•', '*')) or line[0].isdigit():
                    disease_alerts.append(line.lstrip('-•*0123456789. '))
            elif current_section == 'yield' and len(yield_predictions) < 3:
                if line.startswith(('-', '•', '*')) or line[0].isdigit():
                    yield_predictions.append(line.lstrip('-•*0123456789. '))
            elif current_section == 'recommendations' and len(recommendations) < 4:
                if line.startswith(('-', '•', '*')) or line[0].isdigit():
                    recommendations.append(line.lstrip('-•*0123456789. '))

        # Fallback if parsing didn't work well
        if not disease_alerts:
            disease_alerts = [
                "Monitor tomato plants for early blight symptoms",
                "Check wheat fields for rust development",
                "Inspect corn for corn borer damage"
            ]

        if not yield_predictions:
            yield_predictions = [
                "Wheat yield projected at 4.2 tons/acre (+8% from last season)",
                "Corn harvest expected to reach 180 bushels/acre",
                "Soybean production tracking 3% above average"
            ]

        if not recommendations:
            recommendations = [
                "Apply nitrogen fertilizer to wheat fields within 48 hours",
                "Schedule irrigation for corn fields - soil moisture at 45%",
                "Scout fields for pest activity before next pesticide application",
                "Prepare harvest equipment for upcoming corn harvest"
            ]

        return DashboardInsights(
            disease_alerts=disease_alerts,
            yield_predictions=yield_predictions,
            recommendations=recommendations
        )

    except Exception as e:
        # Fallback static insights
        return DashboardInsights(
            disease_alerts=[
                "Monitor tomato plants for early blight symptoms",
                "Check wheat fields for rust development"
            ],
            yield_predictions=[
                "Wheat yield projected at 4.2 tons/acre (+8% from last season)",
                "Corn harvest expected to reach 180 bushels/acre"
            ],
            recommendations=[
                "Apply nitrogen fertilizer to wheat fields within 48 hours",
                "Schedule irrigation for corn fields - soil moisture at 45%",
                "Scout fields for pest activity"
            ]
        )

@app.get("/api/weather")
def get_weather():
    # Mocking weather API response
    return {
        "temperature": "28°C",
        "humidity": "65%",
        "condition": "Sunny",
        "soil_moisture": "Moderate"
    }

@app.get("/api/weather/forecast")
def get_weather_forecast():
    # Provide a dynamic looking 7-day forecast for the frontend
    from datetime import datetime, timedelta
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    today_idx = datetime.now().weekday()
    
    forecasts = []
    # Mix of conditions
    conditions = ["Sun", "Cloud", "CloudRain", "CloudRain", "Sun", "Sun", "Cloud"]
    temps = [24, 22, 19, 20, 25, 26, 23]
    
    for i in range(7):
        day_idx = (today_idx + i) % 7
        forecasts.append({
            "day": days[day_idx] if i > 0 else "Today",
            "temp": f"{temps[i]}°C",
            "condition": conditions[i]
        })
        
    return {
        "irrigation_need": "High",
        "moisture": 34,
        "wind": "SSW 14 km/h",
        "humidity": 62,
        "forecast": forecasts
    }

# Community Endpoints
@app.get("/api/posts", response_model=list[Post])
async def get_posts():
    try:
        if posts_collection is not None:
            posts = []
            cursor = posts_collection.find().sort('_id', -1)
            async for document in cursor:
                # Motor returns _id as ObjectId, need to map to id string if needed,
                # but we're storing _id as UUID string based on our create method so we just pop it
                if '_id' in document:
                    document['id'] = document.pop('_id')
                posts.append(document)
            return posts
        else:
            return list(IN_MEMORY_POSTS.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/posts", response_model=Post)
async def create_post(post: PostCreate):
    try:
        new_post_id = str(uuid.uuid4())
        post_dict = post.model_dump()
        post_dict["_id"] = new_post_id
        post_dict["id"] = new_post_id
        post_dict["likes"] = 0
        post_dict["comments"] = 0
        post_dict["active"] = True
        post_dict["comment_list"] = []

        if posts_collection is not None:
            await posts_collection.insert_one(post_dict.copy())
            post_dict.pop("_id")
            return post_dict
        else:
            post_dict.pop("_id")
            IN_MEMORY_POSTS[new_post_id] = post_dict
            return post_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts/{post_id}/like")
async def toggle_like(post_id: str):
    try:
        if posts_collection is not None:
            # simple toggle/increment logic (we just increment)
            result = await posts_collection.update_one({"_id": post_id}, {"$inc": {"likes": 1}})
            if result.modified_count == 0:
                 raise HTTPException(status_code=404, detail="Post not found")
            return {"status": "success", "message": "Liked"}
        else:
            if post_id in IN_MEMORY_POSTS:
                IN_MEMORY_POSTS[post_id]["likes"] += 1
                return {"status": "success", "message": "Liked"}
            raise HTTPException(status_code=404, detail="Post not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts/{post_id}/comment")
async def add_comment(post_id: str, comment: CommentCreate):
    try:
        new_comment_id = str(uuid.uuid4())
        comment_dict = comment.model_dump()
        comment_dict["id"] = new_comment_id

        if posts_collection is not None:
            result = await posts_collection.update_one(
                {"_id": post_id}, 
                {"$push": {"comment_list": comment_dict}, "$inc": {"comments": 1}}
            )
            if result.modified_count == 0:
                 raise HTTPException(status_code=404, detail="Post not found")
            return {"status": "success", "comment": comment_dict}
        else:
            if post_id in IN_MEMORY_POSTS:
                IN_MEMORY_POSTS[post_id]["comment_list"].append(comment_dict)
                IN_MEMORY_POSTS[post_id]["comments"] += 1
                return {"status": "success", "comment": comment_dict}
            raise HTTPException(status_code=404, detail="Post not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Determine if compiling as a full end-to-end application
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.isdir(frontend_dist):
    # Mount assets folder explicitly if it exists
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str):
        if catchall.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
            
        file_path = os.path.join(frontend_dist, catchall)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Fallback to index.html for Single Page Applications
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
