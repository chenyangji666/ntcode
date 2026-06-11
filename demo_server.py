"""
Flask SQL 注入演示服务器
包含多个故意漏洞的接口，配合 sql_injection_test.py 学习 SQL 注入原理

启动: pip install flask && python demo_server.py
"""

import sqlite3
import hashlib
from flask import Flask, request, jsonify, g

app = Flask(__name__)


# ============================================================
# 数据库初始化
# ============================================================
def init_db():
    db = sqlite3.connect("demo.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            secret_flag TEXT
        )
    """)
    db.execute("DELETE FROM users")
    db.execute("DELETE FROM products")
    db.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin')")
    db.execute("INSERT OR IGNORE INTO users VALUES (2, 'user1', 'password1', 'user')")
    db.execute("INSERT OR IGNORE INTO users VALUES (3, 'user2', 'password2', 'user')")
    db.execute("INSERT OR IGNORE INTO products VALUES (1, 'Widget', 9.99, 'FLAG{sqli_master}')")
    db.execute("INSERT OR IGNORE INTO products VALUES (2, 'Gadget', 19.99, 'FLAG{injection_king}')")
    db.execute("INSERT OR IGNORE INTO products VALUES (3, 'Thingy', 29.99, 'FLAG{data_leaked}')")
    db.commit()
    db.close()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("demo.db")
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db:
        db.close()


# ============================================================
# 漏洞接口
# ============================================================

# ── 1. 字符型注入登录（有漏洞） ──
@app.route("/login", methods=["POST"])
def login_vulnerable():
    """有漏洞的登录 —— 直接拼接用户输入"""
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    db = get_db()
    sql = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    try:
        row = db.execute(sql).fetchone()
        if row:
            return jsonify({"status": "success", "user": dict(row), "sql": sql})
        return jsonify({"status": "fail", "sql": sql})
    except Exception as e:
        return jsonify({"status": "error", "sql": sql, "error": str(e)})


# ── 2. 安全登录（对比） ──
@app.route("/login-safe", methods=["POST"])
def login_safe():
    """安全的登录 —— 参数化查询"""
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    db = get_db()
    sql = "SELECT * FROM users WHERE username=? AND password=?"
    try:
        row = db.execute(sql, (username, password)).fetchone()
        if row:
            return jsonify({"status": "success", "user": dict(row)})
        return jsonify({"status": "fail"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})


# ── 3. 搜索接口（数字型注入） ──
@app.route("/search")
def search_vulnerable():
    """有漏洞的搜索 —— 数字型参数，无引号包裹"""
    product_id = request.args.get("id", "1")
    db = get_db()
    sql = f"SELECT * FROM products WHERE id = {product_id}"
    try:
        rows = db.execute(sql).fetchall()
        return jsonify({
            "sql": sql,
            "results": [dict(r) for r in rows],
        })
    except Exception as e:
        return jsonify({"sql": sql, "error": str(e)})


# ── 4. LIKE 搜索（字符型，有漏洞） ──
@app.route("/search-name")
def search_name_vulnerable():
    """有漏洞的 LIKE 搜索 —— 字符串拼接"""
    keyword = request.args.get("q", "")
    db = get_db()
    sql = f"SELECT * FROM products WHERE name LIKE '%{keyword}%'"
    try:
        rows = db.execute(sql).fetchall()
        return jsonify({
            "sql": sql,
            "results": [dict(r) for r in rows],
        })
    except Exception as e:
        return jsonify({"sql": sql, "error": str(e)})


# ── 5. 用户资料接口（路径参数注入） ──
@app.route("/user/<uid>")
def user_profile_vulnerable(uid):
    """有漏洞的用户查询 —— URL 路径参数拼接"""
    db = get_db()
    sql = f"SELECT id, username, role FROM users WHERE id = {uid}"
    try:
        rows = db.execute(sql).fetchall()
        return jsonify({
            "sql": sql,
            "results": [dict(r) for r in rows],
        })
    except Exception as e:
        return jsonify({"sql": sql, "error": str(e)})


# ── 6. 排序接口（ORDER BY 注入） ──
@app.route("/products")
def products_sortable():
    """有漏洞的排序 —— ORDER BY 拼接"""
    sort_by = request.args.get("sort", "id")
    order = request.args.get("order", "ASC")
    db = get_db()
    sql = f"SELECT id, name, price FROM products ORDER BY {sort_by} {order}"
    try:
        rows = db.execute(sql).fetchall()
        return jsonify({
            "sql": sql,
            "results": [dict(r) for r in rows],
        })
    except Exception as e:
        return jsonify({"sql": sql, "error": str(e)})


# ============================================================
# 首页 — 测试面板
# ============================================================
@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>SQL 注入测试平台</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: 'Segoe UI', monospace; background: #0d1117; color: #c9d1d9;
                   padding: 20px; max-width: 900px; margin: auto; }
            h1 { color: #58a6ff; margin-bottom: 10px; }
            .warning { background: #da3633; color: white; padding: 10px; border-radius: 6px; margin-bottom: 20px; }
            .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px;
                    padding: 16px; margin-bottom: 16px; }
            .card h3 { color: #f78166; margin-bottom: 8px; }
            label { display: block; margin: 6px 0 2px; color: #8b949e; font-size: 13px; }
            input, select { width: 100%; padding: 8px; background: #0d1117; color: #c9d1d9;
                            border: 1px solid #30363d; border-radius: 4px; font-family: monospace; }
            button { margin-top: 10px; padding: 8px 20px; background: #238636; color: white;
                     border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
            button:hover { background: #2ea043; }
            pre { background: #0d1117; padding: 12px; border-radius: 4px; overflow-x: auto;
                  margin-top: 10px; font-size: 12px; border: 1px solid #30363d; max-height: 300px; overflow-y: auto; }
            .payload { background: #1a1a2e; padding: 4px 8px; border-radius: 3px; color: #7ee787;
                       cursor: pointer; user-select: all; }
            .payload:hover { background: #2a2a4e; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            @media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <h1>SQL Injection Test Lab</h1>
        <div class="warning"><strong>警告：</strong>此服务器包含故意漏洞，仅用于本地安全教学。切勿部署到公网！</div>

        <!-- 登录注入 -->
        <div class="card">
            <h3>1. 字符型注入 - 登录绕过</h3>
            <p style="font-size:13px;color:#8b949e">POST /login &nbsp;|&nbsp; 常用 Payload:
                <span class="payload" onclick="document.getElementById('login_user').value=this.textContent">' OR '1'='1</span>
                <span class="payload" onclick="document.getElementById('login_user').value=this.textContent">admin'--</span>
                <span class="payload" onclick="document.getElementById('login_user').value=this.textContent">' UNION SELECT 1,2,3,4--</span>
            </p>
            <div class="grid">
                <div>
                    <label>Username</label>
                    <input id="login_user" value="admin">
                    <label>Password</label>
                    <input id="login_pass" value="admin123">
                    <button onclick="testLogin()">Login (漏洞版)</button>
                    <button onclick="testLoginSafe()" style="background:#1f6feb">Login (安全版)</button>
                </div>
                <div><pre id="login_result">// 结果</pre></div>
            </div>
        </div>

        <!-- 数字型注入 -->
        <div class="card">
            <h3>2. 数字型注入 - 产品搜索</h3>
            <p style="font-size:13px;color:#8b949e">GET /search?id= &nbsp;|&nbsp; Payload:
                <span class="payload" onclick="document.getElementById('search_id').value=this.textContent">1 OR 1=1</span>
                <span class="payload" onclick="document.getElementById('search_id').value=this.textContent">-1 UNION SELECT 1,username,password,role FROM users</span>
            </p>
            <div class="grid">
                <div>
                    <label>Product ID</label>
                    <input id="search_id" value="1">
                    <button onclick="testSearch()">查询</button>
                </div>
                <div><pre id="search_result">// 结果</pre></div>
            </div>
        </div>

        <!-- LIKE 注入 -->
        <div class="card">
            <h3>3. LIKE 注入 - 名称搜索</h3>
            <p style="font-size:13px;color:#8b949e">GET /search-name?q= &nbsp;|&nbsp; Payload:
                <span class="payload" onclick="document.getElementById('search_q').value=this.textContent">' UNION SELECT 1,username,password,role FROM users--</span>
            </p>
            <div class="grid">
                <div>
                    <label>Keyword</label>
                    <input id="search_q" value="Widget">
                    <button onclick="testSearchName()">搜索</button>
                </div>
                <div><pre id="search_name_result">// 结果</pre></div>
            </div>
        </div>

        <!-- ORDER BY 注入 -->
        <div class="card">
            <h3>4. ORDER BY 注入 - 排序</h3>
            <p style="font-size:13px;color:#8b949e">GET /products?sort=&order= &nbsp;|&nbsp; Payload:
                <span class="payload" onclick="document.getElementById('sort_field').value=this.textContent">
                    (CASE WHEN (SELECT length(password) FROM users WHERE username='admin')=8 THEN price ELSE name END)
                </span>
            </p>
            <div class="grid">
                <div>
                    <label>Sort by</label>
                    <input id="sort_field" value="id">
                    <label>Order</label>
                    <select id="sort_order"><option>ASC</option><option>DESC</option></select>
                    <button onclick="testSort()">排序</button>
                </div>
                <div><pre id="sort_result">// 结果</pre></div>
            </div>
        </div>

        <script>
            async function postJSON(url, body) {
                const fd = new FormData();
                for (const [k, v] of Object.entries(body)) fd.append(k, v);
                const r = await fetch(url, { method: "POST", body: fd });
                const data = await r.json();
                document.getElementById(body.result_el).textContent = JSON.stringify(data, null, 2);
                return data;
            }
            async function getJSON(url, el) {
                const r = await fetch(url);
                const data = await r.json();
                document.getElementById(el).textContent = JSON.stringify(data, null, 2);
                return data;
            }

            function testLogin() {
                postJSON("/login", {
                    username: document.getElementById("login_user").value,
                    password: document.getElementById("login_pass").value,
                    result_el: "login_result",
                });
            }
            function testLoginSafe() {
                postJSON("/login-safe", {
                    username: document.getElementById("login_user").value,
                    password: document.getElementById("login_pass").value,
                    result_el: "login_result",
                });
            }
            function testSearch() {
                getJSON(`/search?id=${encodeURIComponent(document.getElementById("search_id").value)}`, "search_result");
            }
            function testSearchName() {
                getJSON(`/search-name?q=${encodeURIComponent(document.getElementById("search_q").value)}`, "search_name_result");
            }
            function testSort() {
                getJSON(`/products?sort=${encodeURIComponent(document.getElementById("sort_field").value)}&order=${document.getElementById("sort_order").value}`, "sort_result");
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("  SQL 注入演示服务器已启动")
    print("  打开浏览器访问: http://localhost:5000")
    print("  按 Ctrl+C 退出")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
