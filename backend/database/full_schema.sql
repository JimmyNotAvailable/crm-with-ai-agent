create table analytics_queue
(
    id         char(36)                          default uuid()               not null
        primary key,
    data_kind  varchar(64)                                                    not null,
    payload    longtext collate utf8mb4_bin                                   not null
        check (json_valid(`payload`)),
    status     enum ('PENDING', 'SENT', 'ERROR') default 'PENDING'            not null,
    created_at datetime(6)                       default current_timestamp(6) not null,
    sent_at    datetime(6)                                                    null,
    error_msg  text                                                           null
)
    collate = utf8mb4_unicode_ci;

create table audience_segments
(
    id         char(36) default uuid() not null
        primary key,
    code       varchar(64)             not null,
    name       varchar(255)            not null,
    filter_sql text                    null,
    constraint code
        unique (code)
)
    collate = utf8mb4_unicode_ci;

create table categories
(
    id          char(36) default uuid() not null
        primary key,
    code        varchar(64)             not null,
    name        varchar(255)            not null,
    description text                    null,
    constraint code
        unique (code)
)
    collate = utf8mb4_unicode_ci;

create table channels
(
    id          char(36) default uuid()                                                    not null
        primary key,
    type        enum ('WEBCHAT', 'EMAIL', 'PHONE', 'FACEBOOK', 'ZALO', 'DISCORD', 'OTHER') not null,
    external_id varchar(255)                                                               null,
    name        varchar(255)                                                               null
)
    collate = utf8mb4_unicode_ci;

create table corpora
(
    id          char(36) default uuid() not null
        primary key,
    name        varchar(255)            not null,
    description text                    null
)
    collate = utf8mb4_unicode_ci;

create table data_retention_policies
(
    id             char(36)   default uuid() not null
        primary key,
    entity         varchar(64)               not null,
    retention_days int                       not null,
    active         tinyint(1) default 1      not null,
    check (`retention_days` > 0)
)
    collate = utf8mb4_unicode_ci;

create table documents
(
    id         char(36) default uuid()      not null
        primary key,
    corpus_id  char(36)                     not null,
    uri        text                         not null,
    meta       longtext collate utf8mb4_bin null
        check (json_valid(`meta`)),
    indexed_at datetime(6)                  null,
    constraint fk_doc_corpus
        foreign key (corpus_id) references corpora (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table kb_tags
(
    id   char(36) default uuid() not null
        primary key,
    name varchar(128)            not null,
    constraint name
        unique (name)
)
    collate = utf8mb4_unicode_ci;

create table kpi_definitions
(
    id          char(36) default uuid() not null
        primary key,
    code        varchar(64)             not null,
    name        varchar(255)            not null,
    description text                    null,
    unit        varchar(32)             null,
    agg_fn      varchar(32)             not null,
    constraint code
        unique (code)
)
    collate = utf8mb4_unicode_ci;

create table alert_rules
(
    id             char(36)                                                                   default uuid()    not null
        primary key,
    kpi_id         char(36)                                                                                     not null,
    op             enum ('>', '>=', '<', '<=', '=', '!=')                                                       not null,
    threshold      decimal(18, 6)                                                                               not null,
    window_minutes int                                                                        default 15        not null,
    severity       enum ('INFO', 'WARN', 'CRITICAL')                                                            not null,
    active         tinyint(1)                                                                 default 1         not null,
    notify_channel enum ('WEBCHAT', 'EMAIL', 'PHONE', 'FACEBOOK', 'ZALO', 'DISCORD', 'OTHER') default 'DISCORD' not null,
    constraint fk_ar_kpi
        foreign key (kpi_id) references kpi_definitions (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table alerts
(
    id        char(36)    default uuid()               not null
        primary key,
    rule_id   char(36)                                 not null,
    fired_at  datetime(6) default current_timestamp(6) not null,
    kpi_value decimal(18, 6)                           null,
    context   longtext collate utf8mb4_bin             null
        check (json_valid(`context`)),
    constraint fk_alert_rule
        foreign key (rule_id) references alert_rules (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table kpi_samples
(
    id        char(36) default uuid()      not null
        primary key,
    kpi_id    char(36)                     not null,
    ts        datetime(6)                  not null,
    value     decimal(18, 6)               not null,
    dimension longtext collate utf8mb4_bin null
        check (json_valid(`dimension`)),
    constraint uq_kpi_ts_dim
        unique (kpi_id, ts),
    constraint fk_kpis_kpi
        foreign key (kpi_id) references kpi_definitions (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_kpi_samples_kpi_ts
    on kpi_samples (kpi_id, ts);

create table ml_models
(
    id         char(36)    default uuid()               not null
        primary key,
    name       varchar(128)                             not null,
    version    varchar(64)                              not null,
    created_at datetime(6) default current_timestamp(6) not null,
    constraint uq_model_name_ver
        unique (name, version)
)
    collate = utf8mb4_unicode_ci;

create table permissions
(
    id   char(36) default uuid() not null
        primary key,
    code varchar(96)             not null,
    name varchar(255)            not null,
    constraint code
        unique (code),
    check (`code` regexp '^[A-Z_.]{3,96}$')
)
    collate = utf8mb4_unicode_ci;

create table predictions
(
    id           char(36)    default uuid()               not null
        primary key,
    model_id     char(36)                                 not null,
    entity_table varchar(64)                              not null,
    entity_id    char(36)                                 not null,
    label        varchar(64)                              not null,
    score        decimal(4, 3)                            null,
    created_at   datetime(6) default current_timestamp(6) not null,
    constraint fk_pred_model
        foreign key (model_id) references ml_models (id)
            on delete cascade,
    check (`score` >= 0 and `score` <= 1)
)
    collate = utf8mb4_unicode_ci;

create index idx_predictions_entity
    on predictions (entity_table, entity_id);

create table products
(
    id          char(36)    default uuid()               not null
        primary key,
    sku         varchar(128)                             not null,
    name        varchar(255)                             not null,
    price       decimal(12, 2)                           not null,
    description text                                     null,
    image_url   text                                     null,
    category_id char(36)                                 null,
    created_at  datetime(6) default current_timestamp(6) not null,
    updated_at  datetime(6) default current_timestamp(6) not null on update current_timestamp(6),
    constraint sku
        unique (sku),
    constraint fk_prod_cat
        foreign key (category_id) references categories (id)
            on delete set null,
    check (`price` >= 0)
)
    collate = utf8mb4_unicode_ci;

create table rag_health_snapshots
(
    id             char(36)                     default uuid()               not null
        primary key,
    corpus_id      char(36)                                                  not null,
    snapshot_at    datetime(6)                  default current_timestamp(6) not null,
    total_docs     int                          default 0                    not null,
    indexed_docs   int                          default 0                    not null,
    stale_docs     int                          default 0                    not null,
    avg_latency_ms int                                                       null,
    coverage_pct   decimal(5, 2)                                             null,
    status         enum ('OK', 'WARN', 'ERROR') default 'OK'                 not null,
    meta           longtext collate utf8mb4_bin                              null
        check (json_valid(`meta`)),
    constraint fk_rhs_corpus
        foreign key (corpus_id) references corpora (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table roles
(
    id   char(36) default uuid() not null
        primary key,
    code varchar(64)             not null,
    name varchar(255)            not null,
    constraint code
        unique (code),
    check (`code` regexp '^[A-Z_]{3,64}$')
)
    collate = utf8mb4_unicode_ci;

create table role_permissions
(
    role_id char(36) not null,
    perm_id char(36) not null,
    primary key (role_id, perm_id),
    constraint fk_rp_perm
        foreign key (perm_id) references permissions (id)
            on delete cascade,
    constraint fk_rp_role
        foreign key (role_id) references roles (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table routing_rules
(
    id        char(36) default uuid()      not null
        primary key,
    code      varchar(64)                  not null,
    name      varchar(255)                 not null,
    priority  int      default 100         not null,
    predicate longtext collate utf8mb4_bin not null
        check (json_valid(`predicate`)),
    action    longtext collate utf8mb4_bin not null
        check (json_valid(`action`)),
    constraint code
        unique (code)
)
    collate = utf8mb4_unicode_ci;

create table ticket_tags
(
    id          char(36) default uuid() not null
        primary key,
    name        varchar(128)            not null,
    description text                    null,
    constraint name
        unique (name)
)
    collate = utf8mb4_unicode_ci;

create table users
(
    id            char(36)                             default uuid()               not null
        primary key,
    email         varchar(320)                                                      not null,
    password_hash text                                                              not null,
    full_name     varchar(255)                                                      not null,
    phone         varchar(50)                                                       null,
    status        enum ('ACTIVE', 'LOCKED', 'PENDING') default 'ACTIVE'             not null,
    created_at    datetime(6)                          default current_timestamp(6) not null,
    updated_at    datetime(6)                          default current_timestamp(6) not null on update current_timestamp(6),
    constraint email
        unique (email)
)
    collate = utf8mb4_unicode_ci;

create table addresses
(
    id         char(36)    default uuid()               not null
        primary key,
    user_id    char(36)                                 not null,
    label      varchar(100)                             null,
    line1      varchar(255)                             not null,
    line2      varchar(255)                             null,
    city       varchar(120)                             not null,
    state      varchar(120)                             null,
    postal     varchar(30)                              null,
    country    varchar(2)  default 'VN'                 not null,
    is_default tinyint(1)  default 0                    not null,
    created_at datetime(6) default current_timestamp(6) not null,
    updated_at datetime(6) default current_timestamp(6) not null on update current_timestamp(6),
    constraint fk_addr_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table audit_logs
(
    id           char(36)    default uuid()               not null
        primary key,
    actor_id     char(36)                                 null,
    action       varchar(64)                              not null,
    target_table varchar(64)                              null,
    target_id    char(36)                                 null,
    details      longtext collate utf8mb4_bin             null
        check (json_valid(`details`)),
    created_at   datetime(6) default current_timestamp(6) not null,
    constraint fk_audit_actor
        foreign key (actor_id) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table consents
(
    id          char(36)    default uuid()                                         not null
        primary key,
    user_id     char(36)                                                           not null,
    kind        enum ('EMAIL_MARKETING', 'SMS_MARKETING', 'TRACKING', 'PII_SHARE') not null,
    granted     tinyint(1)                                                         not null,
    captured_at datetime(6) default current_timestamp(6)                           not null,
    source      varchar(255)                                                       null,
    constraint fk_consents_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table customer_profiles
(
    user_id       char(36)                                 not null
        primary key,
    registered_at datetime(6) default current_timestamp(6) not null,
    loyalty_point int         default 0                    not null,
    dob           date                                     null,
    gender        enum ('M', 'F', 'O')                     null,
    constraint fk_cust_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table customer_tags
(
    id          char(36)    default uuid()               not null
        primary key,
    code        varchar(64)                              not null,
    name        varchar(255)                             not null,
    description text                                     null,
    created_at  datetime(6) default current_timestamp(6) not null,
    created_by  char(36)                                 null,
    constraint code
        unique (code),
    constraint fk_ctag_creator
        foreign key (created_by) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table customer_tag_links
(
    customer_id char(36)                                 not null,
    tag_id      char(36)                                 not null,
    created_at  datetime(6) default current_timestamp(6) not null,
    created_by  char(36)                                 null,
    primary key (customer_id, tag_id),
    constraint fk_ctl_creator
        foreign key (created_by) references users (id)
            on delete set null,
    constraint fk_ctl_customer
        foreign key (customer_id) references users (id)
            on delete cascade,
    constraint fk_ctl_tag
        foreign key (tag_id) references customer_tags (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table erasure_requests
(
    id           char(36)                                              default uuid()               not null
        primary key,
    user_id      char(36)                                                                           not null,
    status       enum ('REQUESTED', 'IN_PROGRESS', 'DONE', 'REJECTED') default 'REQUESTED'          not null,
    requested_at datetime(6)                                           default current_timestamp(6) not null,
    processed_at datetime(6)                                                                        null,
    note         text                                                                               null,
    constraint fk_erase_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table journeys
(
    id         char(36)                                                  default uuid()               not null
        primary key,
    name       varchar(255)                                                                           not null,
    status     enum ('DRAFT', 'ACTIVE', 'PAUSED', 'STOPPED', 'ARCHIVED') default 'DRAFT'              not null,
    created_by char(36)                                                                               null,
    created_at datetime(6)                                               default current_timestamp(6) not null,
    constraint fk_j_created_by
        foreign key (created_by) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table campaign_messages
(
    id         char(36)                                                                   default uuid()  not null
        primary key,
    journey_id char(36)                                                                                   null,
    subject    varchar(255)                                                                               not null,
    body_html  mediumtext                                                                                 not null,
    channel    enum ('WEBCHAT', 'EMAIL', 'PHONE', 'FACEBOOK', 'ZALO', 'DISCORD', 'OTHER') default 'EMAIL' not null,
    constraint fk_cm_journey
        foreign key (journey_id) references journeys (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table campaign_sends
(
    id           char(36)                          default uuid()               not null
        primary key,
    message_id   char(36)                                                       not null,
    to_user_id   char(36)                                                       not null,
    status       enum ('QUEUED', 'SENT', 'FAILED') default 'QUEUED'             not null,
    scheduled_at datetime(6)                       default current_timestamp(6) null,
    sent_at      datetime(6)                                                    null,
    provider_ref varchar(255)                                                   null,
    constraint fk_cs_msg
        foreign key (message_id) references campaign_messages (id)
            on delete cascade,
    constraint fk_cs_user
        foreign key (to_user_id) references users (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_campaign_sends_user_status
    on campaign_sends (to_user_id, status);

create table journey_enrollments
(
    id          char(36)                                          default uuid()               not null
        primary key,
    journey_id  char(36)                                                                       not null,
    user_id     char(36)                                                                       not null,
    enrolled_at datetime(6)                                       default current_timestamp(6) not null,
    status      enum ('RUNNING', 'COMPLETED', 'EXITED', 'PAUSED') default 'RUNNING'            not null,
    constraint uq_journey_user
        unique (journey_id, user_id),
    constraint fk_je_en_journey
        foreign key (journey_id) references journeys (id)
            on delete cascade,
    constraint fk_je_en_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table journey_nodes
(
    id         char(36) default uuid()                                                              not null
        primary key,
    journey_id char(36)                                                                             not null,
    type       enum ('ENTRY', 'FILTER', 'WAIT', 'ACTION_EMAIL', 'ACTION_SMS', 'ACTION_TAG', 'EXIT') not null,
    config     longtext collate utf8mb4_bin                                                         not null
        check (json_valid(`config`)),
    constraint fk_jn_journey
        foreign key (journey_id) references journeys (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table journey_edges
(
    id          char(36) default uuid()      not null
        primary key,
    journey_id  char(36)                     not null,
    from_node   char(36)                     not null,
    to_node     char(36)                     not null,
    `condition` longtext collate utf8mb4_bin null
        check (json_valid(`condition`)),
    constraint fk_je_fromnode
        foreign key (from_node) references journey_nodes (id)
            on delete cascade,
    constraint fk_je_journey
        foreign key (journey_id) references journeys (id)
            on delete cascade,
    constraint fk_je_tonode
        foreign key (to_node) references journey_nodes (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table kb_articles
(
    id         char(36)    default uuid()               not null
        primary key,
    code       varchar(64)                              null,
    title      varchar(255)                             not null,
    body_md    mediumtext                               not null,
    created_by char(36)                                 null,
    created_at datetime(6) default current_timestamp(6) not null,
    updated_at datetime(6) default current_timestamp(6) not null on update current_timestamp(6),
    is_public  tinyint(1)  default 1                    not null,
    constraint code
        unique (code),
    constraint fk_kb_created_by
        foreign key (created_by) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table kb_article_revisions
(
    id         char(36)    default uuid()               not null
        primary key,
    article_id char(36)                                 not null,
    version    int                                      not null,
    title      varchar(255)                             not null,
    body_md    mediumtext                               not null,
    edited_by  char(36)                                 null,
    edited_at  datetime(6) default current_timestamp(6) not null,
    constraint uq_kb_rev
        unique (article_id, version),
    constraint fk_kbr_article
        foreign key (article_id) references kb_articles (id)
            on delete cascade,
    constraint fk_kbr_editor
        foreign key (edited_by) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table kb_article_tags
(
    article_id char(36) not null,
    tag_id     char(36) not null,
    primary key (article_id, tag_id),
    constraint fk_kbat_article
        foreign key (article_id) references kb_articles (id)
            on delete cascade,
    constraint fk_kbat_tag
        foreign key (tag_id) references kb_tags (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table kb_feedback
(
    id         char(36)    default uuid()               not null
        primary key,
    article_id char(36)                                 not null,
    user_id    char(36)                                 null,
    helpful    tinyint(1)                               null,
    comment    text                                     null,
    created_at datetime(6) default current_timestamp(6) not null,
    constraint fk_kbf_article
        foreign key (article_id) references kb_articles (id)
            on delete cascade,
    constraint fk_kbf_user
        foreign key (user_id) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table orders
(
    id               char(36)                                                                         default uuid()               not null
        primary key,
    customer_id      char(36)                                                                                                      not null,
    shipping_address char(36)                                                                                                      null,
    created_at       datetime(6)                                                                      default current_timestamp(6) not null,
    status           enum ('PENDING', 'CONFIRMED', 'FULFILLING', 'SHIPPED', 'COMPLETED', 'CANCELLED') default 'PENDING'            not null,
    subtotal_amount  decimal(12, 2)                                                                   default 0.00                 not null,
    shipping_fee     decimal(12, 2)                                                                   default 0.00                 not null,
    discount_amount  decimal(12, 2)                                                                   default 0.00                 not null,
    total_amount     decimal(12, 2)                                                                   default 0.00                 not null,
    payment_method   enum ('CASH', 'BANK_TRANSFER', 'CREDIT_CARD', 'EWALLET')                                                      not null,
    note             text                                                                                                          null,
    constraint fk_orders_address
        foreign key (shipping_address) references addresses (id)
            on delete set null,
    constraint fk_orders_customer
        foreign key (customer_id) references users (id)
)
    collate = utf8mb4_unicode_ci;

create table order_items
(
    id         char(36) default uuid() not null
        primary key,
    order_id   char(36)                not null,
    product_id char(36)                not null,
    quantity   int                     not null,
    unit_price decimal(12, 2)          not null,
    line_total decimal(12, 2) as (`quantity` * `unit_price`) stored,
    constraint fk_oi_order
        foreign key (order_id) references orders (id)
            on delete cascade,
    constraint fk_oi_product
        foreign key (product_id) references products (id),
    check (`quantity` > 0),
    check (`unit_price` >= 0)
)
    collate = utf8mb4_unicode_ci;

create definer = root@localhost trigger trg_oi_after_del
    after delete
    on order_items
    for each row
BEGIN
    UPDATE orders o
    SET subtotal_amount = IFNULL((SELECT SUM(line_total) FROM order_items WHERE order_id=o.id),0),
        total_amount = IFNULL((SELECT SUM(line_total) FROM order_items WHERE order_id=o.id),0) + o.shipping_fee - o.discount_amount
    WHERE o.id = OLD.order_id;
END;

create definer = root@localhost trigger trg_oi_after_ins
    after insert
    on order_items
    for each row
BEGIN
    UPDATE orders o
    SET subtotal_amount = IFNULL((SELECT SUM(line_total) FROM order_items WHERE order_id=o.id),0),
        total_amount  = IFNULL((SELECT SUM(line_total) FROM order_items WHERE order_id=o.id),0) + o.shipping_fee - o.discount_amount
    WHERE o.id = NEW.order_id;
END;

create definer = root@localhost trigger trg_oi_after_upd
    after update
    on order_items
    for each row
BEGIN
    UPDATE orders o
    SET subtotal_amount = IFNULL((SELECT SUM(line_total) FROM order_items WHERE order_id=o.id),0),
        total_amount = IFNULL((SELECT SUM(line_total) FROM order_items WHERE order_id=o.id),0) + o.shipping_fee - o.discount_amount
    WHERE o.id = NEW.order_id;
END;

create index idx_orders_cust_status
    on orders (customer_id, status);

create table payments
(
    id          char(36)                                       default uuid()               not null
        primary key,
    order_id    char(36)                                                                    not null,
    paid_at     datetime(6)                                                                 null,
    method      enum ('CASH', 'BANK_TRANSFER', 'CREDIT_CARD', 'EWALLET')                    not null,
    status      enum ('INIT', 'SUCCESS', 'FAILED', 'REFUNDED') default 'INIT'               not null,
    amount      decimal(12, 2)                                                              not null,
    gateway_ref varchar(255)                                                                null,
    created_at  datetime(6)                                    default current_timestamp(6) not null,
    constraint fk_pay_order
        foreign key (order_id) references orders (id)
            on delete cascade,
    check (`amount` >= 0)
)
    collate = utf8mb4_unicode_ci;

create table pii_access_logs
(
    id              char(36)    default uuid()               not null
        primary key,
    actor_id        char(36)                                 null,
    subject_user_id char(36)                                 null,
    fields          longtext collate utf8mb4_bin             not null
        check (json_valid(`fields`)),
    purpose         varchar(255)                             not null,
    created_at      datetime(6) default current_timestamp(6) not null,
    constraint fk_pii_actor
        foreign key (actor_id) references users (id)
            on delete set null,
    constraint fk_pii_subject
        foreign key (subject_user_id) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table rag_queries
(
    id         char(36)    default uuid()               not null
        primary key,
    user_id    char(36)                                 null,
    question   mediumtext                               not null,
    response   mediumtext                               null,
    created_at datetime(6) default current_timestamp(6) not null,
    constraint fk_ragq_user
        foreign key (user_id) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table rag_feedback
(
    id         char(36)    default uuid()               not null
        primary key,
    query_id   char(36)                                 not null,
    helpful    tinyint(1)                               null,
    comment    text                                     null,
    created_at datetime(6) default current_timestamp(6) not null,
    constraint fk_ragfb_query
        foreign key (query_id) references rag_queries (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table returns
(
    id           char(36)                                                         default uuid()               not null
        primary key,
    order_id     char(36)                                                                                      not null,
    reason       text                                                                                          null,
    status       enum ('REQUESTED', 'APPROVED', 'REJECTED', 'REFUNDED', 'CLOSED') default 'REQUESTED'          not null,
    requested_at datetime(6)                                                      default current_timestamp(6) not null,
    processed_at datetime(6)                                                                                   null,
    constraint fk_ret_order
        foreign key (order_id) references orders (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table segment_memberships
(
    id         char(36)                               default uuid()               not null
        primary key,
    segment_id char(36)                                                            not null,
    user_id    char(36)                                                            not null,
    joined_at  datetime(6)                            default current_timestamp(6) not null,
    left_at    datetime(6)                                                         null,
    active     tinyint(1)                             default 1                    not null,
    source     enum ('AUTOMATIC', 'MANUAL', 'IMPORT') default 'AUTOMATIC'          not null,
    constraint uq_seg_user_active
        unique (segment_id, user_id, active),
    constraint fk_segm_segment
        foreign key (segment_id) references audience_segments (id)
            on delete cascade,
    constraint fk_segm_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table shipments
(
    id           char(36)                                                                    default uuid()    not null
        primary key,
    order_id     char(36)                                                                                      not null,
    carrier      varchar(255)                                                                                  null,
    tracking_no  varchar(255)                                                                                  null,
    status       enum ('CREATED', 'PICKED', 'IN_TRANSIT', 'DELIVERED', 'FAILED', 'RETURNED') default 'CREATED' not null,
    shipped_at   datetime(6)                                                                                   null,
    delivered_at datetime(6)                                                                                   null,
    constraint fk_ship_order
        foreign key (order_id) references orders (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table staff_profiles
(
    user_id       char(36)               not null
        primary key,
    employee_code varchar(128)           not null,
    position      varchar(128)           not null,
    hired_at      date default curdate() not null,
    constraint employee_code
        unique (employee_code),
    constraint fk_staff_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table tickets
(
    id          char(36)                                          default uuid()               not null
        primary key,
    customer_id char(36)                                                                       not null,
    channel_id  char(36)                                                                       null,
    subject     varchar(255)                                                                   not null,
    content     text                                                                           not null,
    created_at  datetime(6)                                       default current_timestamp(6) not null,
    status      enum ('NEW', 'IN_PROGRESS', 'RESOLVED', 'CLOSED') default 'NEW'                not null,
    priority    enum ('LOW', 'MEDIUM', 'HIGH', 'URGENT')          default 'MEDIUM'             not null,
    assignee_id char(36)                                                                       null,
    constraint fk_tk_agent
        foreign key (assignee_id) references users (id)
            on delete set null,
    constraint fk_tk_channel
        foreign key (channel_id) references channels (id)
            on delete set null,
    constraint fk_tk_customer
        foreign key (customer_id) references users (id)
)
    collate = utf8mb4_unicode_ci;

create table conversations
(
    id         char(36)    default uuid()               not null
        primary key,
    ticket_id  char(36)                                 null,
    started_at datetime(6) default current_timestamp(6) not null,
    ended_at   datetime(6)                              null,
    constraint fk_conv_ticket
        foreign key (ticket_id) references tickets (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table messages
(
    id              char(36)    default uuid()               not null
        primary key,
    conversation_id char(36)                                 null,
    sender_id       char(36)                                 null,
    kind            enum ('CHATBOT', 'AGENT', 'CUSTOMER')    not null,
    content         text                                     not null,
    sent_at         datetime(6) default current_timestamp(6) not null,
    channel_id      char(36)                                 null,
    constraint fk_msg_channel
        foreign key (channel_id) references channels (id)
            on delete set null,
    constraint fk_msg_conv
        foreign key (conversation_id) references conversations (id)
            on delete cascade,
    constraint fk_msg_sender
        foreign key (sender_id) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create table attachments
(
    id         char(36) default uuid() not null
        primary key,
    message_id char(36)                not null,
    file_name  varchar(255)            not null,
    mime_type  varchar(127)            not null,
    url        text                    not null,
    size_bytes bigint                  null,
    constraint fk_att_msg
        foreign key (message_id) references messages (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table interaction_events
(
    id         char(36)    default uuid()               not null
        primary key,
    user_id    char(36)                                 null,
    ticket_id  char(36)                                 null,
    message_id char(36)                                 null,
    raw_text   text                                     null,
    created_at datetime(6) default current_timestamp(6) not null,
    constraint fk_ie_msg
        foreign key (message_id) references messages (id)
            on delete set null,
    constraint fk_ie_ticket
        foreign key (ticket_id) references tickets (id)
            on delete set null,
    constraint fk_ie_user
        foreign key (user_id) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

create index idx_messages_conv_time
    on messages (conversation_id, sent_at);

create table sentiments
(
    id            char(36)    default uuid()                        not null
        primary key,
    event_id      char(36)                                          not null,
    label         enum ('NEGATIVE', 'NEUTRAL', 'POSITIVE', 'MIXED') not null,
    score         decimal(4, 3)                                     null,
    model_version varchar(64)                                       not null,
    inferred_at   datetime(6) default current_timestamp(6)          not null,
    constraint event_id
        unique (event_id),
    constraint fk_sent_event
        foreign key (event_id) references interaction_events (id)
            on delete cascade,
    check (`score` >= 0 and `score` <= 1)
)
    collate = utf8mb4_unicode_ci;

create table ticket_tag_links
(
    ticket_id char(36) not null,
    tag_id    char(36) not null,
    primary key (ticket_id, tag_id),
    constraint fk_ttl_tag
        foreign key (tag_id) references ticket_tags (id)
            on delete cascade,
    constraint fk_ttl_ticket
        foreign key (ticket_id) references tickets (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_tickets_cust_status
    on tickets (customer_id, status);

create table user_roles
(
    user_id char(36) not null,
    role_id char(36) not null,
    primary key (user_id, role_id),
    constraint fk_ur_role
        foreign key (role_id) references roles (id)
            on delete cascade,
    constraint fk_ur_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_users_statuss
    on users (status);

create table warehouses
(
    id      char(36) default uuid() not null
        primary key,
    name    varchar(255)            not null,
    address text                    null
)
    collate = utf8mb4_unicode_ci;

create table inventory
(
    warehouse_id char(36)      not null,
    product_id   char(36)      not null,
    quantity     int default 0 not null,
    primary key (warehouse_id, product_id),
    constraint fk_inv_prod
        foreign key (product_id) references products (id)
            on delete cascade,
    constraint fk_inv_wh
        foreign key (warehouse_id) references warehouses (id)
            on delete cascade,
    check (`quantity` >= 0)
)
    collate = utf8mb4_unicode_ci;

create table webhooks
(
    id         char(36)   default uuid() not null
        primary key,
    name       varchar(255)              not null,
    target_url text                      not null,
    secret     varchar(255)              null,
    active     tinyint(1) default 1      not null
)
    collate = utf8mb4_unicode_ci;

create table webhook_events
(
    id           char(36)                           default uuid()    not null
        primary key,
    webhook_id   char(36)                                             not null,
    topic        varchar(128)                                         not null,
    payload      longtext collate utf8mb4_bin                         not null
        check (json_valid(`payload`)),
    delivered_at datetime(6)                                          null,
    status       enum ('PENDING', 'SENT', 'FAILED') default 'PENDING' not null,
    error_msg    text                                                 null,
    constraint fk_whe_webhook
        foreign key (webhook_id) references webhooks (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create table work_queues
(
    id   char(36) default uuid() not null
        primary key,
    code varchar(64)             not null,
    name varchar(255)            not null,
    constraint code
        unique (code)
)
    collate = utf8mb4_unicode_ci;

create table assignments
(
    id              char(36)    default uuid()               not null
        primary key,
    ticket_id       char(36)                                 not null,
    queue_id        char(36)                                 null,
    assignee_id     char(36)                                 null,
    decided_by_rule char(36)                                 null,
    decided_at      datetime(6) default current_timestamp(6) not null,
    constraint fk_asg_queue
        foreign key (queue_id) references work_queues (id)
            on delete set null,
    constraint fk_asg_rule
        foreign key (decided_by_rule) references routing_rules (id)
            on delete set null,
    constraint fk_asg_ticket
        foreign key (ticket_id) references tickets (id)
            on delete cascade,
    constraint fk_asg_user
        foreign key (assignee_id) references users (id)
            on delete set null
)
    collate = utf8mb4_unicode_ci;

