# scripts/sql (Microservices DB)

Thư mục này dùng mô hình **1 lớp**: chỉ giữ các file SQL **schema (source-of-truth)**.

## Schema (source-of-truth)
- `scripts/sql/01_identity_db.sql` … `07_marketing_db.sql`
- Vai trò:
	- Tạo **DDL** (tables/views/triggers)
	- (Nếu cần) tạo **baseline data** ở mức hệ thống (vd: roles/permissions, categories/channels mặc định…)
- Đây là “hợp đồng dữ liệu” của từng service DB.

## Nguyên tắc: không auto-seed operational/demo data
- Không còn `scripts/sql/seeds/` và không còn mount `02_seed.sql`.
- Dữ liệu vận hành (users/products/orders/tickets…) sẽ được tạo theo 1 trong các cách:
	- chạy luồng của Backend qua API (register/create CRUD)
	- chạy script riêng (nếu bạn muốn bootstrap dữ liệu)
	- hoặc migration/app init (tuỳ cách bạn quản trị dữ liệu)

## Docker init flow
Trong [docker/docker-compose.yml](../..//docker/docker-compose.yml), mỗi DB chỉ mount:
- `/docker-entrypoint-initdb.d/01_schema.sql`  ⟵ schema

Để rebuild sạch microservices DB:

```bash
cd docker
docker compose --profile microservices down -v
docker compose --profile microservices up -d
```
