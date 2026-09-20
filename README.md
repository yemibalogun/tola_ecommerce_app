# Tola

A multi-tenant e-commerce platform. Anyone can sign up, get their own storefront
at a shareable link, customise how it looks, and sell from it.

## How multi-tenancy works

Everything a seller owns hangs off a `Tenant` (a store). A `User` with
`is_admin` belongs to exactly one tenant and can only ever see that tenant's
data — products, categories, orders, banners and settings are all scoped by
`tenant_id`.

A store is reachable two ways:

| URL                            | Resolved by                                    |
| ------------------------------ | ---------------------------------------------- |
| `/store/<slug>/`               | `app/store` blueprint, from the path           |
| `https://<slug>.yourdomain.com` | `load_current_tenant` in `app/__init__.py`     |

The path form is the one shown to sellers, because it works everywhere with no
DNS setup. The subdomain form keeps working if it is configured; requests to
`/` on a store subdomain render that store's homepage.

Shoppers do not need an account, and each store keeps its own cart in the
session (`session["carts"][<tenant_id>]`), so items never cross between stores.

## Routes at a glance

- `/` — platform landing page (or the store homepage on a store subdomain)
- `/signup` — creates a store and its owner account in one step
- `/admin/auth/login` — seller sign in
- `/admin/dashboard` — metrics, setup checklist and the shareable store link
- `/admin/tenant/settings` — customise branding, hero, currency and contact info
- `/admin/tenant/banners` — hero slides for the store homepage
- `/store/<slug>/…` — the public storefront

## Store customisation

From **Customise store**, an owner controls their store name and link, logo,
tagline, about text, accent colour, light/dark homepage theme, currency, hero
headline and image, and contact details. The accent colour drives the whole
storefront palette through the `--accent` CSS custom property; everything else
is derived from it with `color-mix`.

Hero headlines support one piece of markup: wrap a word in asterisks to paint it
with the accent gradient, e.g. `Elevate Your *Audio* Journey`.

## Orders

Checkout persists a real `Order` plus one `OrderItem` per line, inside a single
transaction. Shoppers do not need an account: `order.user_id` is null for guests
and the buyer's name, email, phone and delivery address are stored on the order,
so the owner can fulfil it from **Orders** in the dashboard. Line items snapshot
`unit_price`, so later price changes never rewrite order history. New orders
start as `pending`; dashboard revenue only counts `paid` and `completed`.

Taking payment is still to do — nothing is charged at checkout.

## Running locally

```bash
python -m venv venv
venv/Scripts/activate          # Windows; use source venv/bin/activate elsewhere
pip install -r requirements.txt

# .env needs DATABASE_URL and SECRET_KEY
flask db upgrade               # applies any pending migrations
flask run --port 5057
```

`docker-compose up` brings up Postgres and the app together. `.env` ships with
the local Postgres URL; the `db` hostname used inside docker-compose is kept
there as a comment.

### About the schema

In development the app bootstraps a **completely empty** database with
`db.create_all()` and then stamps it at the latest Alembic revision. Once tables
exist it never touches them again — the schema belongs to migrations from that
point on, so run `flask db upgrade` after pulling schema changes.

> **Known gap:** the migration chain has no initial "create tables" revision —
> the oldest migration already assumes a `product` table exists. So
> `flask db upgrade` cannot build a database from nothing; that is what the
> bootstrap above covers. Worth squashing into a real baseline migration before
> deploying anywhere new.

## Layout

```
app/
  admin/      seller dashboard (products, categories, orders, inventory)
  api/        JSON endpoints
  store/      public per-tenant storefront
  web/        platform landing, signup, store customisation
  models/     SQLAlchemy models
  static/css/ tola.css (storefront + platform), admin/css/admin.css
  templates/  store/, platform/, auth/, admin/, partials/
```
