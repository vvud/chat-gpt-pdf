from langchain.vectorstores.chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.schema import HumanMessage, AIMessage
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response, make_response, send_from_directory
from flask_cors import CORS
from functools import wraps


def make_chain():
    model = ChatOpenAI(
        # model_name="gpt-4",
        # model_name="gpt-4-turbo-preview",
        model_name="gpt-3.5-turbo",
        verbose=True
    )
    embedding = OpenAIEmbeddings()

    vector_store = Chroma(
        collection_name="honda-book",
        embedding_function=embedding,
        persist_directory="data/chroma",
    )

    return ConversationalRetrievalChain.from_llm(
        model,
        retriever=vector_store.as_retriever(),
        return_source_documents=True,
        verbose=True,
    )

 
def process_question(question):
    # Generate answer
    response = chain({"question": question, "chat_history": chat_history})

    # Retrieve answer
    answer = response["answer"]
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=answer))
    
    return answer   


ACCESS_TOKEN = 'demo'
API_TOKEN = 'api-demo'

def require_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if 'Authorization' in request.headers:
            token = request.headers.get('Authorization')

        if not token or not token.startswith('Bearer '):
            return jsonify({'message': 'Missing or invalid token'}), 401
        
        if token != f"Bearer {API_TOKEN}":
            return jsonify({'message': 'Invalid token'}), 401

        return func(*args, **kwargs)

    return decorated


app = Flask(__name__)
CORS(app)

app.config['JSON_AS_ASCII'] = False

@app.route("/")
def serve_static():
    return send_from_directory('web', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    # Replace 'build/static' with the path to your static files inside the build folder
    return send_from_directory('web', path)


@app.route('/api/code/verify', methods=['POST'])
def verify_code():
   # get data from body.question
    access_code = request.json.get('access_code')

    if not access_code:
        return Response(status=400)
    
    try:
        is_valid = True if access_code == ACCESS_TOKEN else False
        return make_response(jsonify(is_valid), 201)
    except:
        return Response(status=409)
    
    
@app.route('/api/chat/response', methods=['POST'])
@require_token
def response():
   # get data from body.question
    question = request.json.get('question')

    if not question:
        return Response(status=400)
    
    try:
        response = process_question(question)
        print("Response: ", response)
        return make_response(jsonify({'data': response}), 201)
    except:
        return Response(status=409)

    
if __name__ == "__main__":
    load_dotenv()

    chain = make_chain()
    chat_history = []
    app.run(host='0.0.0.0', port=int(6969), debug=True)
