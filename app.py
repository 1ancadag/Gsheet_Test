from flask import Flask, request, jsonify
import clickhouse_connect

app = Flask(__name__)

# === ClickHouse connection details ===
CLICKHOUSE_HOST = '10.13.188.201'
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = 'default'
CLICKHOUSE_PASSWORD = '@tpbi234'


client = clickhouse_connect.get_client(
    host=CLICKHOUSE_HOST,
    port=CLICKHOUSE_PORT,
    username=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD
)


@app.route('/')
def home():
    return "✅ Flask API is running. Use POST /query to get data."


@app.route('/query', methods=['POST'])
def query_data():
    try:
        print("📥 Headers:", dict(request.headers))
        print("📦 Raw Body:", request.data)
        json_data = request.get_json(force=True)
        print("✅ Parsed JSON:", json_data)
    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 400

    return jsonify({"test": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
