import sys
import json
import urllib.request
import urllib.parse
import io

# Ensure UTF-8 output on Windows console
sys.stdout.reconfigure(encoding='utf-8')

def test_health():
    req = urllib.request.Request("http://127.0.0.1:8000/health")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("=== 1. HEALTH CHECK ===")
        print(json.dumps(data, indent=2))
        return data

def test_query(label, query_text):
    payload = json.dumps({"query": query_text}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/query",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"\n=== {label} ===")
        print(f"Query: {query_text}")
        print(f"Answer: {data['answer']}")
        print(f"Grounded: {data['grounded']}, Confidence Score: {data['confidence_score']}")
        t = data['timing']
        print(f"Timing Breakdown (ms): Total={t['total_pipeline_ms']:.2f}, Embed={t['query_embedding_ms']:.2f}, VectorSearch={t['vector_search_ms']:.3f}, Gate={t['answerability_check_ms']:.3f}, Gen={t['llm_generation_ms']:.3f}")
        print(f"Sources Count: {len(data['sources'])}")
        if data['sources']:
            top = data['sources'][0]
            print(f"Top Source: [{top['chunk_id']}] (score: {top['score']:.4f}, lang: {top['language']})")
            print(f"Excerpt: {top['text'][:120]}...")
        return data

def test_voice(label, audio_bytes, filename="audio.wav", language="hin_Deva"):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = bytearray()
    
    # File field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: audio/wav\r\n\r\n")
    body.extend(audio_bytes)
    body.extend(b"\r\n")
    
    # Language field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(b'Content-Disposition: form-data; name="language"\r\n\r\n')
    body.extend(language.encode("utf-8"))
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/voice/ask",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"\n=== {label} ===")
        print(f"Transcript: {data['transcript']}")
        print(f"Answer: {data['answer']}")
        print(f"Grounded: {data['grounded']}, Confidence Score: {data['confidence_score']}")
        t = data['timing']
        print(f"Timing Breakdown (ms): Total={t['total_pipeline_ms']:.2f}, STT={t['stt_ms']:.2f}, Post-STT RAG={(t['total_pipeline_ms'] - t['stt_ms']):.2f}, Embed={t['query_embedding_ms']:.2f}, Search={t['vector_search_ms']:.3f}")
        return data

if __name__ == "__main__":
    print("Testing Live FastAPI Server Integration...")
    test_health()
    test_query("2. ENGLISH TEXT QUERY", "What are the legal liabilities of a corporation?")
    test_query("3. HINDI TEXT QUERY", "कॉर्पोरेशन की कानूनी देनदारियां क्या हैं?")
    test_query("4. BENGALI TEXT QUERY", "কর্পোরেশনের আইনি দায়বদ্ধতা কি কি?")
    
    test_voice("5. VOICE QUERY (Hindi)", b"\xe0\xa4\x95\xe0\xa4\xbe\xe0\xa4\xb0\xe0\xa5\x8d\xe0\xa4\xaa\xe0\xa5\x8b\xe0\xa4\xb0\xe0\xa5\x87\xe0\xa4\xb6\xe0\xa4\xa8 \xe0\xa4\x95\xe0\xa5\x8d\xe0\xa4\xaf\xe0\xa4\xbe \xe0\xa4\xb9\xe0\xa5\x88?", language="hin_Deva")
    test_voice("6. VOICE QUERY (English)", b"What are the legal liabilities of a corporation?", language="eng_Latn")
    test_voice("7. VOICE QUERY (Bengali)", b"\xe0\xa6\x95\xe0\xa6\xb0\xe0\xa5\x8d\xe0\xa6\xaa\xe0\xa7\x8b\xe0\xa6\xb0\xe0\xa7\x87\xe0\xa6\xb6\xe0\xa6\xa8 \xe0\xa6\x95\xe0\xa6\xbf?", language="ben_Beng")
