# -*- coding: utf-8 -*-
"""
高难度校准题二次操纵检查 - 运行脚本
15题 × 3模型 = 45次 API 调用
"""
import json, os, time, hashlib, urllib.request, urllib.error, datetime, openpyxl

BASE = "https://one-hub.hycx-gd.cn/v1/chat/completions"
API_KEY = os.environ.get("COMPANY_API_KEY", "")
TEMPERATURE = 0
MAX_TOKENS = 2000

MODELS = [
    ("A1", "qwen3.8-flash"),
    ("A2", "qwen3.7-max"),
    ("A3", "qwen3.8-max"),
]

DIR = r"E:\实验文件整理_按论文逻辑\experiment-design-3x3\model_calibration_hard15_v1"
Q_FILE = os.path.join(DIR, "calibration_hard15_questions.xlsx")
OUT = os.path.join(DIR, "calibration_hard15_raw_outputs.jsonl")
LOG = os.path.join(DIR, "logs", "hard15_run.log")
os.makedirs(os.path.join(DIR, "logs"), exist_ok=True)

SYSTEM_PROMPT = "你是一个知识与推理能力测试助手。请仔细阅读题目，给出准确、简洁的回答。选择题直接给选项字母和简要理由，计算题给答案和计算过程。不要编造信息。"
OUTPUT_FMT = "请按以下格式回答：\n【答案】\n（直接给出最终答案）\n【推理过程】\n（简要说明推理步骤或计算过程）"

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg + "\n")
    print(msg, flush=True)

def load_jsonl(path):
    out = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                out.append(json.loads(line))
    return out

# 加载题目
wb = openpyxl.load_workbook(Q_FILE, data_only=True)
ws = wb["校准题库"]
headers = [c.value for c in ws[1]]
questions = []
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[0] is None: continue
    q = dict(zip(headers, row))
    questions.append(q)

log(f"加载校准题：{len(questions)} 题")

def call_api(model_name, user_message, retries=3):
    body = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    last_err = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(BASE, data=data, headers={
            "Authorization": "Bearer " + API_KEY,
            "Content-Type": "application/json",
        })
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                out = json.loads(resp.read().decode("utf-8"))
            latency = round(time.time() - t0, 2)
            content = out["choices"][0]["message"].get("content") or ""
            usage = out.get("usage", {})
            finish = out["choices"][0].get("finish_reason")
            status = "OK" if content.strip() and finish == "stop" else ("TRUNCATED" if content.strip() else "EMPTY")
            return {"content": content, "latency": latency, "input_tokens": usage.get("prompt_tokens"),
                    "output_tokens": usage.get("completion_tokens"), "finish_reason": finish, "status": status}
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:300]}"
        if attempt < retries:
            wait = 15 * attempt
            log(f"  attempt{attempt} failed, retry in {wait}s")
            time.sleep(wait)
    return {"content": "", "status": "ERROR", "error": last_err, "latency": None}

# 断点续跑
done = {}
if os.path.exists(OUT):
    for r in load_jsonl(OUT):
        if r.get("status") in ("OK", "TRUNCATED"):
            done[r["run_id"]] = r

total = 0
for q in questions:
    qid = q["题号"]
    q_text = q["题目"]
    for m_code, m_name in MODELS:
        run_id = f"{qid}__{m_code}"
        if run_id in done:
            log(f"[skip] {run_id}")
            continue
        total += 1
        user_msg = f"题目：\n{q_text}\n\n{OUTPUT_FMT}"
        prompt_hash = hashlib.sha256((SYSTEM_PROMPT + "\x00" + user_msg).encode("utf-8")).hexdigest()
        log(f"[run] {run_id} ({m_name}) ...")
        res = call_api(m_name, user_msg)
        row = {
            "run_id": run_id, "question_id": qid, "category": q.get("类别", ""),
            "difficulty": q.get("难度", ""), "model_condition": m_code, "model_name": m_name,
            "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS, "prompt_hash": prompt_hash,
            "gold_answer": q.get("Gold Answer", ""),
            "input_tokens": res.get("input_tokens"), "output_tokens": res.get("output_tokens"),
            "latency": res.get("latency"), "status": res.get("status"),
            "finish_reason": res.get("finish_reason"), "error": res.get("error"),
            "raw_answer": res.get("content"),
        }
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        log(f"[done] {run_id} status={row['status']} out_tokens={row['output_tokens']} latency={row['latency']}s")

rows = load_jsonl(OUT)
ok = [r for r in rows if r["status"] in ("OK", "TRUNCATED")]
failed = [r for r in rows if r["status"] == "ERROR"]
log(f"\n===== 汇总 =====")
log(f"总计：{len(rows)} runs，成功：{len(ok)}，失败：{len(failed)}")
if failed:
    for r in failed:
        log(f"  FAIL {r['run_id']}: {r.get('error','?')[:100]}")
