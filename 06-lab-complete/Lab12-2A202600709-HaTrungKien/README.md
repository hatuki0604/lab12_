# AI Cafe Vibe Recommender

## Overview

Day la backend-first prototype cho bai toan chon cafe bang hinh anh.

Flow hien tai:

1. Backend lay danh sach cafes tu Supabase
2. SigLIP embed anh cafe offline
3. Frontend xin `5` seed cafes random
4. `5` seed nay duoc tao bang cach:
   - random `5` categories
   - moi category random `1` cafe
5. User chon `1` hoac `2` seed cafes
6. Backend tinh cosine similarity tren image embeddings
7. Backend tra top `3` cafes gan nhat
8. Neu user khong thich `5` seed hien tai:
   - frontend goi lai `GET /api/seed-cafes`
   - kem `excluded_seed_cafe_ids`
   - backend random batch seed moi

## Current Runtime Contract

### 1. Get seed cafes

```http
GET /api/seed-cafes
```

Query params:

- `count`: optional, mac dinh lay tu `SEED_COUNT`
- `excluded_seed_cafe_ids`: optional, dung khi user bo qua batch seed cu

Example response:

```json
{
  "seed_cafes": [
    {
      "id": "cafe_001",
      "name": "Fours Bakery Signature",
      "image_url": "https://...",
      "rating": 4.2,
      "address": "87C P. Ly Thuong Kiet, Hoan Kiem, Ha Noi",
      "category": "Bakery cafe",
      "google_maps_url": "https://..."
    }
  ],
  "has_more": true,
  "fallback_message": null
}
```

### 2. Recommend cafes

```http
POST /api/recommend
```

Request:

```json
{
  "selected_seed_cafe_ids": ["cafe_001", "cafe_006"],
  "excluded_result_cafe_ids": []
}
```

Response:

```json
{
  "query_description": "The user prefers a cafe vibe that combines these qualities: ...",
  "selected_seed_cafes": [
    {
      "id": "cafe_001",
      "name": "Fours Bakery Signature",
      "category": "Bakery cafe"
    }
  ],
  "results": [
    {
      "id": "cafe_010",
      "name": "528HZ",
      "image_url": "https://...",
      "rating": 4.7,
      "address": "...",
      "category": "Cafe bar",
      "similarity_score": 0.8932,
      "reason": "Matches your vibe through warm, wooden, cozy, plus a cafe bar atmosphere.",
      "google_maps_url": "https://..."
    }
  ],
  "has_more": true,
  "fallback_message": null
}
```

### 3. Feedback

```http
POST /api/feedback
```

Request:

```json
{
  "selected_seed_cafe_ids": ["cafe_001"],
  "cafe_id": "cafe_010",
  "feedback": "not_my_vibe"
}
```

## Data Flow

### Input data

- `data/cafes.jsonl`
  - du lieu cafes keo ve tu Supabase
  - phai co `id`, `name`, `category`, `image_url`, `google_maps_url`
  - nen co mot trong cac truong mo ta:
    - `description`
    - `caption`
    - `ai_description`

### Generated runtime data

- `data/cafes.json`
  - sau khi preprocess bang SigLIP
  - chua `embedding`
  - backend runtime doc file nay

### Runtime log

- `data/feedback.jsonl`

## Scripts

### 1. Pull cafes from Supabase

```bash
python scripts/supabase_cafes.py
```

Output:

- `data/cafes.jsonl`

### 2. Generate image embeddings with SigLIP

```bash
python scripts/preprocess_cafes.py
```

Output:

- `data/cafes.json`

Note:

- script nay chi dung `SiglipVisionModel` + `SiglipImageProcessor`
- khong can tokenizer va khong can `sentencepiece`

### 3. Validate runtime data

```bash
python scripts/validate_data.py
```

## Run backend

```bash
cd Hackathon
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/supabase_cafes.py
python scripts/preprocess_cafes.py
python scripts/validate_data.py
uvicorn app.main:app --reload
```

## Notes

- Runtime khong goi SigLIP
- Runtime khong goi Supabase
- Runtime chi doc `data/cafes.json`
- `tests/fixtures/` moi la sample data cho test, khong phai runtime data that
