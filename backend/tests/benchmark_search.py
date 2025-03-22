import time
from pathlib import Path
import sys
from sqlalchemy import text

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.db.session import engine


def benchmark_search_queries():
    print("==================================================")
    print("GenericRx PostgreSQL Sub-50ms Search Benchmark")
    print("==================================================")

    test_queries = [
        ("Prefix Search (Exact)", "Telma"),
        ("Prefix Search (Short)", "Pan"),
        ("Typo / Fuzzy (Tlma -> Telma)", "Tlma"),
        ("Typo / Fuzzy (Glycomtt -> Glycomet)", "Glycomtt"),
        ("Combination Drug (Augmentn -> Augmentin)", "Augmentn"),
        ("Typo / Fuzzy (Doloo -> Dolo)", "Doloo"),
        ("Prefix Search (Ato -> Atorva)", "Ato"),
        ("Prefix Search (Rosu -> Rosuvas)", "Rosu"),
    ]

    sql_explain = text(
        """
        EXPLAIN ANALYZE
        SELECT 
            b.id,
            b.brand_name,
            s.salt_name,
            similarity(b.brand_name, :q) AS sml
        FROM branded_medicines b
        JOIN salts s ON b.salt_id = s.id
        WHERE b.brand_name ILIKE :prefix OR b.brand_name % :q
        ORDER BY 
            CASE WHEN b.brand_name ILIKE :prefix THEN 1 ELSE 2 END,
            sml DESC
        LIMIT 10;
        """
    )

    sql_execute = text(
        """
        SELECT 
            b.id,
            b.brand_name,
            s.salt_name,
            similarity(b.brand_name, :q) AS sml
        FROM branded_medicines b
        JOIN salts s ON b.salt_id = s.id
        WHERE b.brand_name ILIKE :prefix OR b.brand_name % :q
        ORDER BY 
            CASE WHEN b.brand_name ILIKE :prefix THEN 1 ELSE 2 END,
            sml DESC
        LIMIT 10;
        """
    )

    latencies = []

    with engine.connect() as conn:
        # Warm up connection
        conn.execute(text("SELECT 1;"))

        for label, query_term in test_queries:
            clean_q = query_term.strip()
            prefix_q = f"{clean_q}%"
            params = {"q": clean_q, "prefix": prefix_q}

            # Measure wall-clock execution latency
            start_time = time.perf_counter()
            result = conn.execute(sql_execute, params).fetchall()
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            latencies.append(latency_ms)

            # Check execution plan
            plan = conn.execute(sql_explain, params).fetchall()
            plan_text = " ".join([str(row[0]) for row in plan])
            used_index = (
                "idx_branded_name_trgm" in plan_text
                or "Bitmap Index Scan" in plan_text
            )

            status = "PASSED (< 50ms)" if latency_ms < 50.0 else "SLOW"
            top_match = result[0][1] if result else "No match"

            print(f"[{status}] {label}: '{query_term}'")
            print(f"   -> Top Match: {top_match}")
            print(
                f"   -> Latency: {latency_ms:.2f} ms | Index Used: {used_index}\n"
            )

    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)

    print("==================================================")
    print(f"Benchmark Results (3,000 Medicines):")
    print(f" -> Average Latency: {avg_latency:.2f} ms")
    print(f" -> Maximum Latency: {max_latency:.2f} ms")
    print(f" -> SLA Target (< 50 ms): {'MET' if max_latency < 50 else 'MISSED'}")
    print("==================================================")


if __name__ == "__main__":
    benchmark_search_queries()