-- AlterTable
ALTER TABLE "Flyer" ADD COLUMN     "contentId" TEXT,
ADD COLUMN     "publishedFrom" TIMESTAMP(3),
ADD COLUMN     "publishedUntil" TIMESTAMP(3);

-- AlterTable
ALTER TABLE "Offer" ADD COLUMN     "contentId" TEXT,
ADD COLUMN     "description" TEXT,
ADD COLUMN     "imageAlt" TEXT,
ADD COLUMN     "imageTitle" TEXT,
ADD COLUMN     "oldPriceFormatted" TEXT,
ADD COLUMN     "pageNumber" INTEGER,
ADD COLUMN     "parentContentId" TEXT,
ADD COLUMN     "priceConditions" TEXT,
ADD COLUMN     "priceFormatted" TEXT,
ADD COLUMN     "priceFrequency" TEXT,
ADD COLUMN     "publisherId" TEXT,
ADD COLUMN     "validFrom" TIMESTAMP(3);

-- CreateIndex
CREATE INDEX "Flyer_contentId_idx" ON "Flyer"("contentId");

-- CreateIndex
CREATE INDEX "Offer_contentId_idx" ON "Offer"("contentId");

-- CreateIndex
CREATE INDEX "Offer_parentContentId_idx" ON "Offer"("parentContentId");
