-- CreateTable
CREATE TABLE "Retailer" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "logoUrl" TEXT,
    "scrapedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Retailer_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Flyer" (
    "id" TEXT NOT NULL,
    "retailerId" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "pages" INTEGER NOT NULL,
    "validFrom" TIMESTAMP(3) NOT NULL,
    "validUntil" TIMESTAMP(3) NOT NULL,
    "url" TEXT NOT NULL,
    "pdfUrl" TEXT,
    "thumbnailUrl" TEXT,
    "scrapedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Flyer_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Store" (
    "id" TEXT NOT NULL,
    "retailerId" TEXT NOT NULL,
    "address" TEXT NOT NULL,
    "city" TEXT NOT NULL,
    "postalCode" TEXT NOT NULL,
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "phone" TEXT,
    "openingHours" TEXT,
    "scrapedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Store_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Product" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "brand" TEXT,
    "category" TEXT,
    "description" TEXT,
    "imageUrl" TEXT,
    "scrapedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Product_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Offer" (
    "id" TEXT NOT NULL,
    "flyerId" TEXT,
    "productId" TEXT,
    "retailerId" TEXT NOT NULL,
    "productName" TEXT NOT NULL,
    "brand" TEXT,
    "category" TEXT,
    "currentPrice" DOUBLE PRECISION NOT NULL,
    "oldPrice" DOUBLE PRECISION,
    "discount" DOUBLE PRECISION,
    "discountPercentage" DOUBLE PRECISION,
    "unitPrice" TEXT,
    "url" TEXT NOT NULL,
    "imageUrl" TEXT,
    "validUntil" TIMESTAMP(3),
    "scrapedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Offer_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ScrapingLog" (
    "id" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "startedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completedAt" TIMESTAMP(3),
    "itemsScraped" INTEGER NOT NULL DEFAULT 0,
    "errors" TEXT,
    "metadata" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ScrapingLog_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Retailer_name_key" ON "Retailer"("name");

-- CreateIndex
CREATE INDEX "Retailer_name_idx" ON "Retailer"("name");

-- CreateIndex
CREATE INDEX "Retailer_category_idx" ON "Retailer"("category");

-- CreateIndex
CREATE UNIQUE INDEX "Flyer_url_key" ON "Flyer"("url");

-- CreateIndex
CREATE INDEX "Flyer_retailerId_idx" ON "Flyer"("retailerId");

-- CreateIndex
CREATE INDEX "Flyer_validFrom_idx" ON "Flyer"("validFrom");

-- CreateIndex
CREATE INDEX "Flyer_validUntil_idx" ON "Flyer"("validUntil");

-- CreateIndex
CREATE INDEX "Flyer_url_idx" ON "Flyer"("url");

-- CreateIndex
CREATE INDEX "Store_retailerId_idx" ON "Store"("retailerId");

-- CreateIndex
CREATE INDEX "Store_city_idx" ON "Store"("city");

-- CreateIndex
CREATE INDEX "Store_postalCode_idx" ON "Store"("postalCode");

-- CreateIndex
CREATE UNIQUE INDEX "Store_retailerId_address_key" ON "Store"("retailerId", "address");

-- CreateIndex
CREATE INDEX "Product_name_idx" ON "Product"("name");

-- CreateIndex
CREATE INDEX "Product_brand_idx" ON "Product"("brand");

-- CreateIndex
CREATE INDEX "Product_category_idx" ON "Product"("category");

-- CreateIndex
CREATE UNIQUE INDEX "Offer_url_key" ON "Offer"("url");

-- CreateIndex
CREATE INDEX "Offer_flyerId_idx" ON "Offer"("flyerId");

-- CreateIndex
CREATE INDEX "Offer_productId_idx" ON "Offer"("productId");

-- CreateIndex
CREATE INDEX "Offer_retailerId_idx" ON "Offer"("retailerId");

-- CreateIndex
CREATE INDEX "Offer_productName_idx" ON "Offer"("productName");

-- CreateIndex
CREATE INDEX "Offer_currentPrice_idx" ON "Offer"("currentPrice");

-- CreateIndex
CREATE INDEX "Offer_validUntil_idx" ON "Offer"("validUntil");

-- CreateIndex
CREATE INDEX "Offer_url_idx" ON "Offer"("url");

-- CreateIndex
CREATE INDEX "ScrapingLog_type_idx" ON "ScrapingLog"("type");

-- CreateIndex
CREATE INDEX "ScrapingLog_status_idx" ON "ScrapingLog"("status");

-- CreateIndex
CREATE INDEX "ScrapingLog_startedAt_idx" ON "ScrapingLog"("startedAt");

-- AddForeignKey
ALTER TABLE "Flyer" ADD CONSTRAINT "Flyer_retailerId_fkey" FOREIGN KEY ("retailerId") REFERENCES "Retailer"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Store" ADD CONSTRAINT "Store_retailerId_fkey" FOREIGN KEY ("retailerId") REFERENCES "Retailer"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Offer" ADD CONSTRAINT "Offer_flyerId_fkey" FOREIGN KEY ("flyerId") REFERENCES "Flyer"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Offer" ADD CONSTRAINT "Offer_productId_fkey" FOREIGN KEY ("productId") REFERENCES "Product"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Offer" ADD CONSTRAINT "Offer_retailerId_fkey" FOREIGN KEY ("retailerId") REFERENCES "Retailer"("id") ON DELETE CASCADE ON UPDATE CASCADE;
