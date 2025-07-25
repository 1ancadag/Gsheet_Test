from flask import Flask, request, jsonify
import clickhouse_connect
import re

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
    data = request.get_json(force=True, silent=True)
    print("Received payload:", data)

    if not data:
        return jsonify({"error": "Invalid JSON or empty request"}), 400

    prf = data.get("prf", "").strip()
    prf = re.sub(r"[^a-zA-Z0-9\- ]", "", prf)

    where_clauses = []
    if prf:
        where_clauses.append(f"toString(`PRF CONTROL NUMBER`) LIKE '%{prf}%'")

    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = "WHERE " + where_sql
    query = f"""
                SELECT
                        toInt32OrNull(`PRF CONTROL NUMBER`) AS `PRF#`,
                        formatDateTime(toDate(parseDateTimeBestEffortOrNull(`PRF REQUEST DATE (MM-DD-YYYY)`)), '%b') AS `MONTH`,
                        toDate(parseDateTimeBestEffortOrNull(`PRF REQUEST DATE (MM-DD-YYYY)`)) AS `PRF REQUEST DATE`,
                        toDate(parseDateTimeBestEffortOrNull(`BHR APPROVED DATE (MM-DD-YYYY)`)) AS `BHR APPROVED DATE`,
                        toInt32OrNull(`STORE CODE`) AS `STORE CODE`,
                        `STORE LOCATION`,
                        `POSITION`,
                        `MUNICIPALITY`,
                        `AREA`,
                        toInt32OrNull(`# OF REQUEST`) AS `# OF REQUEST`,
                        NULL AS `PRF REQUEST BY PART`,
                        `PRF STATUS`,
                        NULL AS `HIRING STATUS`,
                        NULL AS `TP CANDIDATE ID`,
                        NULL AS `APPLICANT NAME`,
                        NULL AS `LAST NAME`,
                        NULL AS `FIRST NAME`,
                        NULL AS `MIDDLE NAME`,
                        `POSITION` AS `Position`,
                        NULL AS ` TA POSITION REMARKS [if changes occurs]`,
                        NULL AS `PENDING REQUIREMENTS [PLS CHECK THE PENDING REQTS]`,
                        NULL AS `CONTACT NUMBER`,
                        NULL AS `EMAIL ADDRESS`,
                        NULL AS `EDUC ATTAIN.`,
                        NULL AS `RETAIL`,
                        NULL AS `RECRUITER`,
                        NULL AS `REQS. SENT DATE`,
                        NULL AS `SOURCE`,
                        NULL AS `DATE HIRED`, 
                        NULL AS `RESUME DATE`,
                        NULL AS `REMARKS`,
                        NULL AS `AGING`,
                        NULL AS `TAT`,
                        formatDateTime(toDate(parseDateTimeBestEffortOrNull(`PRF REQUEST DATE (MM-DD-YYYY)`)), '%b') AS `Month`,
                        NULL AS `FOLDER [TP]`,
                        NULL AS `CANDIDATE / APPLICATION ID`
                    FROM HR_REPORT.STORES_AND_AUX_PLANTILLA_DEMAND
                ORDER BY `PRF#` DESC
                """

    result = client.query(query)
    return jsonify({
        "columns": result.column_names,
        "rows": result.result_rows
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
