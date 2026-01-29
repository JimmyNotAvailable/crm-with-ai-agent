# DataGrip Connection Guide - CRM Microservices

## Quick Setup (Copy & Paste)

### 1. Identity Database (Port 3310)
```
Host:     localhost
Port:     3310
User:     identity_user
Password: identity_pass
Database: crm_identity_db
URL:      jdbc:mysql://localhost:3310/crm_identity_db
```

### 2. Product Database (Port 3311)
```
Host:     localhost
Port:     3311
User:     product_user
Password: product_pass
Database: crm_product_db
URL:      jdbc:mysql://localhost:3311/crm_product_db
```

### 3. Order Database (Port 3312)
```
Host:     localhost
Port:     3312
User:     order_user
Password: order_pass
Database: crm_order_db
URL:      jdbc:mysql://localhost:3312/crm_order_db
```

### 4. Support Database (Port 3313)
```
Host:     localhost
Port:     3313
User:     support_user
Password: support_pass
Database: crm_support_db
URL:      jdbc:mysql://localhost:3313/crm_support_db
```

### 5. Knowledge Database (Port 3314)
```
Host:     localhost
Port:     
User:     knowledge_user
Password: knowledge_pass
Database: crm_knowledge_db
URL:      jdbc:mysql://localhost:3314/crm_knowledge_db
```

### 6. Analytics Database (Port 3315)
```
Host:     localhost
Port:     3315
User:     analytics_user
Password: analytics_pass
Database: crm_analytics_db
URL:      jdbc:mysql://localhost:3315/crm_analytics_db
```

### 7. Marketing Database (Port 3316)
```
Host:     localhost
Port:     3316
User:     marketing_user
Password: marketing_pass
Database: crm_marketing_db
URL:      jdbc:mysql://localhost:3316/crm_marketing_db
```

---

## Root Access (Full Admin)

Nếu cần quyền root để quản trị:

| Database | Root Password |
|----------|---------------|
| Identity | root_identity_pass |
| Product | root_product_pass |
| Order | root_order_pass |
| Support | root_support_pass |
| Knowledge | root_knowledge_pass |
| Analytics | root_analytics_pass |
| Marketing | root_marketing_pass |

---

## Adminer Web Interface

Nếu muốn dùng giao diện web thay vì DataGrip:
- URL: http://localhost:8081
- Server: `mysql-identity` (hoặc mysql-product, mysql-order, ...)
- Username/Password: như trên
