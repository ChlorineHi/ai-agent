from flask import Flask, request, jsonify, send_file, Response, stream_with_context, make_response
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from flask_cors import CORS
from dotenv import load_dotenv
import sqlite3
import json
import time
import zhipuai
import random
from search_utils import search_web
from email_service import EmailRequest, send_email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
from PIL import Image
import io
from utils.math_formatter import MathFormatter
from werkzeug.utils import secure_filename
from openai import OpenAI

# 定义一组有趣的 emoji
EMOJIS = [
    "😊", "🤔", "🎉", "✨", "💡", "🌟", "🚀", "💪", "👍", "🎯",
    "🌈", "🎨", "🎭", "🎪", "🎢", "🎡", "🎠", "🎮", "🎲", "🎯",
    "🎱", "🎳", "🎾", "🏀", "⚽", "🏈", "🏉", "🎿", "🏂", "🏊",
    "🏄", "🚴", "🚵", "🏇", "🏆", "🏅", "🎖", "🏵", "🎗", "🎫"
]

# 加载环境变量
load_dotenv()

app = Flask(__name__)
# 初始化 CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }
}, supports_credentials=True)

# 从环境变量中获取 API 密钥
api_key = os.getenv("ZHIPUAI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "sk-5f5b3406be884ec5be623d95049c5b2f")
openai_api_key = os.getenv("OPENAI_API_KEY", "")

# 初始化客户端
client = zhipuai.ZhipuAI(api_key=api_key) if api_key else None
deepseek_client = OpenAI(
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com"
) if deepseek_api_key else None
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# 初始化 Deepseek 客户端
if deepseek_api_key is None:
    raise ValueError("Deepseek API key not found. Please set the DEEPSEEK_API_KEY environment variable.")

# 初始化向量存储
embeddings = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")
vector_store = None

# 创建格式化器实例
math_formatter = MathFormatter()

# 设置文档保存路径
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testDemo', 'docs')

def initialize_vector_store():
    global vector_store
    # 创建文档目录
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
    
    # 加载文档
    documents = []
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    # 遍历文档目录中的所有文件
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith('.txt'):
            try:
                with open(os.path.join(DOCS_DIR, filename), 'r', encoding='utf-8') as f:
                    text = f.read()
                    documents.extend(text_splitter.split_text(text))
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
    
    if documents:
        try:
            # 创建向量存储
            vector_store = FAISS.from_texts(documents, embeddings)
            print("Vector store initialized successfully")
        except Exception as e:
            print(f"Error initializing vector store: {str(e)}")
            vector_store = None

def preprocess_text(text):
    """
    预处理文本，简化 LaTeX 和 Markdown 格式
    """
    # 替换常见的数学符号
    math_symbols = {
        '\\sum': '∑',
        '\\times': '×',
        '\\div': '÷',
        '\\pm': '±',
        '_i': 'ᵢ',
        '^T': 'ᵀ',
        '^{-1}': '⁻¹',
        '_1': '₁',
        '_2': '₂',
        '_3': '₃',
        '_n': 'ₙ'
    }
    
    # 处理行内数学公式
    if '$$' in text or '$' in text:
        for symbol, replacement in math_symbols.items():
            text = text.replace(symbol, replacement)
        # 移除数学公式定界符
        text = text.replace('$$', '').replace('$', '')
    
    # 简化 Markdown 格式
    text = text.replace('**', '').replace('*', '')  # 移除加粗和斜体标记
    text = text.replace('`', '')  # 移除代码标记
    
    return text

@app.route('/')
def home():
    return 'Flask is running!'

@app.route('/index', methods=['GET', 'POST', 'OPTIONS'])
def chat_api():
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept-Encoding, Accept, Origin'
        return response

    if request.method == 'GET':
        question = request.args.get('question')
    elif request.is_json:
        user_input = request.json
        question = user_input.get('question')
    else:
        try:
            user_input = request.data.decode('utf-8')
            question = user_input
        except Exception as e:
            return jsonify({'error': 'Invalid request data'}), 400

    if not question:
        return jsonify({'error': 'Question is required'}), 400

    def generate():
        try:
            print("Starting stream generation...")
            
            if vector_store is not None:
                # 使用向量存储检索相关文档
                docs = vector_store.similarity_search(question, k=3)
                context = "\n".join([doc.page_content for doc in docs])
                
                # 构建带有上下文的提示
                messages = [
                    {"role": "system", "content": """你是一个智能助手。请基于以下参考资料回答问题。如果问题与参考资料无关，你可以基于自己的知识回答。

在回答涉及数学内容时，请遵循以下规则：
1. 使用简单直观的符号表示数学公式，避免复杂的LaTeX格式
2. 对于简单的数学符号，直接使用Unicode字符（如：×, ÷, ±, ≤, ≥, α, β, λ等）
3. 对于上下标，使用简单的形式（如：x₁, x², aᵢ等）
4. 分数使用斜杠表示（如：a/b）
5. 避免使用复杂的LaTeX环境和命令

参考资料：
""" + context},
                    {"role": "user", "content": question}
                ]
            else:
                # 如果没有向量存储，使用普通对话
                messages = [
                    {"role": "system", "content": """你是一个智能助手，可以帮助用户解答问题。

在回答涉及数学内容时，请遵循以下规则：
1. 使用简单直观的符号表示数学公式，避免复杂的LaTeX格式
2. 对于简单的数学符号，直接使用Unicode字符（如：×, ÷, ±, ≤, ≥, α, β, λ等）
3. 对于上下标，使用简单的形式（如：x₁, x², aᵢ等）
4. 分数使用斜杠表示（如：a/b）
5. 避免使用复杂的LaTeX环境和命令"""},
                    {"role": "user", "content": question}
                ]
            
            model = request.args.get('model', 'zhipu')  # 默认使用智谱AI模型
            
            # 根据选择的模型调用不同的API
            if model == 'zhipu':
                # 智谱AI的处理逻辑
                response = client.chat.completions.create(
                    model="glm-4v-flash",
                    messages=messages,
                    stream=True,
                    temperature=0.7,
                )
            elif model == 'deepseek':
                # Deepseek的处理逻辑
                response = deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.7,
                    stream=True
                )
            else:
                return jsonify({'error': 'Invalid model selection'}), 400

            initial_data = 'data: {"content": "", "done": false}\n\n'
            yield initial_data
            
            full_response = ""
            chunk_count = 0
            
            for chunk in response:
                try:
                    chunk_count += 1
                    if hasattr(chunk.choices[0].delta, 'content'):
                        content = chunk.choices[0].delta.content
                        if content:
                            try:
                                content_stripped = content.rstrip()
                                if content_stripped:
                                    is_sentence_end = content_stripped[-1] in ["。", "！", "？"]
                                    if is_sentence_end and random.random() < 0.2:
                                        content += random.choice(EMOJIS)
                            except IndexError as e:
                                print(f"Error processing content for emoji: {e}")
                            
                            full_response += content
                            data = json.dumps({
                                'content': content,
                                'done': False
                            }, ensure_ascii=False)
                            yield f"data: {data}\n\n"
                            time.sleep(0.05)
                except Exception as chunk_error:
                    print(f"Error processing chunk: {chunk_error}")
                    continue
                
            print(f"Stream completed. Total chunks: {chunk_count}")
                
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            error_data = json.dumps({'error': str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
        finally:
            try:
                final_data = json.dumps({"content": "", "done": True}, ensure_ascii=False)
                yield f'data: {final_data}\n\n'
            except Exception as final_error:
                print(f"Error sending final data: {final_error}")

    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': 'http://localhost:5173',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept-Encoding, Accept, Origin',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'X-Accel-Buffering': 'no'
    }
    
    return Response(
        stream_with_context(generate()),
        headers=headers
    )

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_document():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        print("Received upload request")
        
        if 'file' not in request.files:
            print("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        print(f"Received file: {file.filename}")
        
        if file.filename == '':
            print("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if not file.filename.endswith('.txt'):
            print("Invalid file type")
            return jsonify({'error': 'Only .txt files are supported'}), 400
        
        # 确保docs目录存在
        if not os.path.exists(DOCS_DIR):
            print(f"Creating docs directory: {DOCS_DIR}")
            os.makedirs(DOCS_DIR)
        
        # 保存文件
        file_path = os.path.join(DOCS_DIR, file.filename)
        print(f"Saving file to: {file_path}")
        file.save(file_path)
        print(f"File saved successfully: {file_path}")
        
        # 重新初始化向量存储
        print("Initializing vector store...")
        initialize_vector_store()
        print("Vector store initialization completed")
        
        response = jsonify({'message': 'File uploaded and processed successfully'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        error_response = jsonify({'error': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        error_response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return error_response, 500

# 允许的文件类型
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_knowledge', methods=['POST', 'OPTIONS'])
def upload_knowledge():
    try:
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            return response

        if 'file' not in request.files:
            return jsonify({'error': '没有文件部分'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                # 确保docs目录存在
                os.makedirs(DOCS_DIR, exist_ok=True)
                # 保存到docs目录
                file_path = os.path.join(DOCS_DIR, filename)
                file.save(file_path)
                print(f"文件已保存到: {file_path}")  # 添加日志
                return jsonify({'message': '文件上传成功', 'filename': filename}), 200
            except Exception as e:
                print(f"保存文件时出错: {str(e)}")  # 添加错误日志
                return jsonify({'error': f'保存文件时出错: {str(e)}'}), 500
        
        return jsonify({'error': '不支持的文件类型'}), 400
    except Exception as e:
        print(f"上传处理时出错: {str(e)}")  # 添加错误日志
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/chat')
def chat_interface():
    return send_file('chat.html')

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('query')
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        results = search_web(query)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-email', methods=['POST'])
def handle_send_email():
    """处理邮件发送请求"""
    try:
        data = request.get_json()
        email_request = EmailRequest(**data)
        
        # 同步方式调用邮件发送函数
        send_email_sync(email_request)
        return jsonify({"status": "success", "message": "邮件发送成功"})
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def send_email_sync(email_request: EmailRequest):
    """同步方式发送邮件"""
    try:
        msg = create_email_message(email_request)
        
        # 连接SMTP服务器
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # 启用TLS加密
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"发送邮件时出错: {str(e)}")
        raise e

def create_email_message(email_request: EmailRequest):
    """创建邮件消息"""
    msg = MIMEMultipart()
    msg['From'] = email_request.from_addr
    msg['To'] = email_request.to_addr
    msg['Subject'] = email_request.subject
    msg.attach(MIMEText(email_request.content, 'plain', 'utf-8'))
    return msg

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', ''))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        data = request.json
        if not data or 'messages' not in data:
            return jsonify({'error': 'Messages are required'}), 400

        messages = data['messages']
        model = data.get('model', 'zhipu')  # 默认使用 zhipu 模型

        # 检查客户端是否已初始化
        if model == 'zhipu' and not client:
            return jsonify({'error': 'Zhipu API key not configured'}), 500
        elif model == 'deepseek' and not deepseek_client:
            return jsonify({'error': 'Deepseek API key not configured'}), 500

        # 根据选择的模型使用不同的 API
        if model == 'zhipu':
            response = client.chat.completions.create(
                model="glm-4",
                messages=[{"role": msg["role"], "content": msg["content"]} for msg in messages],
                temperature=0.7,
                stream=True
            )
        elif model == 'deepseek':
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": msg["role"], "content": msg["content"]} for msg in messages],
                temperature=0.7,
                stream=True,
                max_tokens=1024
            )
            
        def generate():
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat_with_image', methods=['POST', 'OPTIONS'])
def chat_with_image():
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Accept-Encoding, Origin'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    try:
        print("Received chat_with_image request")
        print("Files:", request.files)
        print("Form:", request.form)
        
        if 'image' not in request.files:
            print("No image file in request")
            return jsonify({'error': '请提供图片'}), 400
            
        if 'question' not in request.form:
            print("No question in request")
            return jsonify({'error': '请提供问题'}), 400

        image_file = request.files['image']
        question = request.form['question']
        
        if not image_file:
            print("Empty image file")
            return jsonify({'error': '图片文件为空'}), 400
        
        print(f"Processing image: {image_file.filename}")
        print(f"Question: {question}")

        # 读取图片并转换为base64
        try:
            image = Image.open(image_file)
            print(f"Image mode: {image.mode}, size: {image.size}")
            
            # 统一转换为RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
                print("Converted image to RGB mode")
            
            # 调整图片大小以适应API限制
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            print(f"Resized image to: {image.size}")
            
            # 将图片转换为base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            print("Successfully converted image to base64")
            print(f"Base64 string length: {len(img_str)}")
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return jsonify({'error': f'图片处理失败: {str(e)}'}), 500

        try:
            print("Preparing request to ZhipuAI")
            # 准备发送给智谱AI的消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_str}"
                            }
                        }
                    ]
                }
            ]
            
            print("Sending request to ZhipuAI")
            # 调用智谱AI的API
            response = client.chat.completions.create(
                model="glm-4v-flash",  # 使用支持图像的模型
                messages=messages,
                max_tokens=1024,
                temperature=0.7
            )
            print("Received response from ZhipuAI")

            # 获取AI的回复
            ai_response = response.choices[0].message.content
            print(f"AI Response: {ai_response}")

            return jsonify({
                'response': preprocess_text(ai_response)
            })

        except Exception as e:
            print(f"Error calling ZhipuAI API: {str(e)}")
            error_message = str(e)
            if "API key" in error_message:
                error_message = "API密钥无效或未设置"
            return jsonify({'error': f'调用AI服务失败: {error_message}'}), 500

    except Exception as e:
        print(f"Unexpected error in chat_with_image: {str(e)}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

# 数据库相关代码
def init_db():
    conn = sqlite3.connect('compusers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS compusers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    try:
        c.execute("INSERT INTO compusers (username, password) VALUES (?, ?)", ("test", "test123"))
        c.execute("INSERT INTO compusers (username, password) VALUES (?, ?)", ("admin", "admin123"))
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing username or password'}), 400
        
        conn = sqlite3.connect('compusers.db')
        c = conn.cursor()
        c.execute("SELECT * FROM compusers WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            response = jsonify({'message': 'Login successful'})
            return response
        else:
            response = jsonify({'error': 'Invalid username or password'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 401
            
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.errorhandler(Exception)
def handle_error(error):
    print(f"Global error handler: {error}")
    response = jsonify({'error': str(error)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 500

if __name__ == '__main__':
    initialize_vector_store()
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)