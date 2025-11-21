# راهنمای تنظیم Supabase

## دریافت Connection String

1. به [Supabase Dashboard](https://supabase.com/dashboard) بروید
2. پروژه `xyfybgmxmfazziusnyqq` را انتخاب کنید
3. به **Settings** → **Database** بروید
4. در بخش **Connection string**، یکی از این موارد را انتخاب کنید:
   - **URI** (برای development)
   - **Connection Pooling** (برای production - توصیه می‌شود)

## تنظیم .env.local

فایل `.env.local` را باز کنید و `[YOUR-PASSWORD]` را با password دیتابیس خود جایگزین کنید:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xyfybgmxmfazziusnyqq.supabase.co:5432/postgres?sslmode=require
```

یا برای connection pooling (توصیه می‌شود):

```env
DATABASE_URL=postgresql://postgres.xyfybgmxmfazziusnyqq:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
```

## اجرای Migrations

بعد از تنظیم `DATABASE_URL`، migrations را اجرا کنید:

```bash
# ایجاد migration
npx prisma migrate dev --name init

# یا اگر migration از قبل وجود دارد
npx prisma migrate deploy
```

## تنظیم در Vercel

برای production، `DATABASE_URL` را در Vercel Dashboard تنظیم کنید:
1. به Vercel Dashboard بروید
2. پروژه را انتخاب کنید
3. **Settings** → **Environment Variables**
4. `DATABASE_URL` را با connection string Supabase اضافه کنید

