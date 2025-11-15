# Using the Graph Analytics UI - Step-by-Step Guide

## ✅ Data Status

**Current Database:** 522 meaningful reservations (problematic data removed)

### Data Summary:
- **Time Range:** June 1, 2025 - November 30, 2025 (6 months)
- **Total Revenue:** RM 180,741.66 (from completed stays)
- **Completed Stays:** 422 reservations
- **Upcoming Bookings:** 36 confirmed reservations
- **Active Check-ins:** 4 guests currently staying

### Monthly Performance:
| Month | Stays | Revenue (RM) | Status |
|-------|-------|--------------|--------|
| June 2025 | 73 | 31,785.16 | ✅ Peak season |
| July 2025 | 68 | 30,222.72 | ✅ Strong |
| August 2025 | 96 | **40,343.60** | ⭐ **Best month** |
| September 2025 | 67 | 28,252.18 | ✅ Steady |
| October 2025 | 91 | 38,979.38 | ✅ Peak season |
| November 2025 | 31 | 11,158.62 | 🔄 Current (partial) |

### Room Type Performance:
| Room Type | Stays | Total Revenue | Avg per Booking | Market Share |
|-----------|-------|---------------|----------------|--------------|
| Suite | 107 | RM 65,587.50 | RM 612.97 | 36.4% |
| Standard | 211 | RM 64,782.96 | RM 307.03 | 35.9% |
| Deluxe | 108 | RM 50,371.20 | RM 466.40 | 27.9% |

---

## 📊 How to Generate Graphs via UI

### Step 1: Launch the Application
```bash
python run.py
```

### Step 2: Navigate to Analytics
1. Main window will open
2. Look for **"Analytics"** menu or button
3. Click **"Revenue Analytics by Room Type"**

### Step 3: Configure Graph Parameters

The UI dialog shows these options:

#### **Analysis Parameters:**

1. **Start Date:** `2025-06-01` (June 1, 2025)
   - This is when your sample data begins
   - You can select any date in the range

2. **End Date:** `2025-11-30` (November 30, 2025)
   - This is the end of your sample data
   - You can narrow the range if needed

3. **Time Bucket:** Choose how to group data
   - **`daily`** - Day-by-day analysis (good for short periods)
   - **`weekly`** - Week-by-week trends (good for 1-3 months)
   - **`monthly`** ⭐ **RECOMMENDED** - Month-by-month (best for 6-month view)
   - **`quarterly`** - Quarter-by-quarter (for annual views)

4. **Chart Type:** Choose visualization style
   - **`trend`** - Line chart showing average cost per reservation
   - **`bar`** - Bar chart showing total revenue
   - **`combined`** ⭐ **RECOMMENDED** - Both trend and bar charts together

### Step 4: Generate the Graph

1. Click **"Generate"** button
2. Wait a few seconds for processing
3. A success message will appear
4. Charts are saved to `reports/` folder

### Step 5: View Your Analytics

**Charts Generated:**
- 📈 PNG image file with visualization
- 📊 CSV data file for Excel/spreadsheet analysis

**File Naming:**
```
revenue_by_room_type_{time_bucket}_{start_date}_{end_date}_{timestamp}.png
revenue_by_room_type_{time_bucket}_{start_date}_{end_date}_{timestamp}.csv
```

**Example:**
```
revenue_by_room_type_monthly_2025-06-01_2025-11-30_20251113_105523.png
revenue_by_room_type_monthly_2025-06-01_2025-11-30_20251113_105523.csv
```

---

## 🎯 Recommended Graph Configurations

### For Overall Business Performance:
```yaml
Start Date: 2025-06-01
End Date: 2025-11-30
Time Bucket: monthly
Chart Type: combined
```
**Shows:** 6-month overview with trends and totals

### For Detailed Recent Analysis:
```yaml
Start Date: 2025-11-01
End Date: 2025-11-30
Time Bucket: daily
Chart Type: combined
```
**Shows:** Day-by-day November performance

### For Weekly Patterns:
```yaml
Start Date: 2025-06-01
End Date: 2025-11-30
Time Bucket: weekly
Chart Type: trend
```
**Shows:** Week-over-week average booking values

### For Peak Season Focus:
```yaml
Start Date: 2025-08-01
End Date: 2025-10-31
Time Bucket: weekly
Chart Type: bar
```
**Shows:** Peak season (Aug-Oct) weekly revenue

---

## 📈 What You'll See in the Graphs

### Combined Chart (Recommended):

**Top Panel - Trend Line Chart:**
- X-axis: Time periods (months/weeks/days)
- Y-axis: Average cost per reservation (RM)
- Lines: One per room type (Suite, Standard, Deluxe)
- **Insights:** Which room types command higher prices

**Bottom Panel - Bar Chart:**
- X-axis: Time periods
- Y-axis: Total revenue (RM)
- Bars: Grouped by room type with different colors
- **Insights:** Which periods and room types generate most revenue

### Key Insights You'll Gain:

1. **Revenue Trends:**
   - Is revenue growing or declining?
   - Which months are strongest?
   - Seasonal patterns

2. **Room Performance:**
   - Which room type is most profitable?
   - Average booking value by type
   - Volume vs. value analysis

3. **Business Opportunities:**
   - When to increase prices (high demand)
   - When to run promotions (low demand)
   - Which room types to prioritize

---

## 🔍 Interpreting Your Results

### Based on Current Sample Data:

#### **Monthly Trends:**
- ✅ August is your **peak month** (RM 40,343.60)
- ✅ Strong performance in June, October
- ⚠️ November is slower (partial month data)

**Action:** Charge premium rates in August/October

#### **Room Type Performance:**
- ✅ **Suite rooms** generate highest total revenue (36.4% share)
- ✅ **Standard rooms** have most bookings (211 stays)
- ✅ Suite rooms have **2x higher** average value (RM 613 vs RM 307)

**Action:** Focus marketing on Suite rooms, offer Standard→Suite upgrades

#### **Seasonal Patterns:**
- ✅ Summer peak (June-August): 237 stays, RM 102,351
- ✅ Fall strong (September-October): 158 stays, RM 67,232
- ⚠️ Late fall slowdown (November): 31 stays, RM 11,159

**Action:** Plan staff and inventory around these patterns

---

## 💡 Troubleshooting

### "No data available"
- Check your date range includes completed stays
- Ensure dates are in format: YYYY-MM-DD
- Verify reservations exist in that period

### "Generate button not working"
- Check all fields are filled
- Ensure start date is before end date
- Look for error messages in console

### "Chart looks empty"
- Try a different time bucket (e.g., monthly instead of daily)
- Expand your date range
- Verify reservations have status "Checked-Out" or "Checked-In"

### "Want different date range"
- You can analyze any period from June 1 - Nov 30, 2025
- Use daily bucket for 1-30 days
- Use weekly bucket for 1-3 months  
- Use monthly bucket for 3+ months

---

## 🎯 Quick Start Examples

### Example 1: Complete Overview
**Goal:** See overall 6-month performance

**Settings:**
- Start: `2025-06-01`
- End: `2025-11-30`
- Bucket: `monthly`
- Type: `combined`

**Expected Result:**
- 6 months of data
- Clear seasonal trends
- Room type comparison
- Files saved to `reports/`

### Example 2: Recent Performance
**Goal:** Analyze current month

**Settings:**
- Start: `2025-11-01`
- End: `2025-11-30`
- Bucket: `daily`
- Type: `combined`

**Expected Result:**
- Daily breakdown of November
- Current performance vs historical
- Files saved to `reports/`

### Example 3: Peak Season Analysis
**Goal:** Understand best months

**Settings:**
- Start: `2025-08-01`
- End: `2025-10-31`
- Bucket: `weekly`
- Type: `bar`

**Expected Result:**
- Week-by-week revenue for peak season
- Total revenue by room type
- Files saved to `reports/`

---

## 📁 Where to Find Your Charts

After generating:

1. **Navigate to reports folder:**
   ```
   hotel_digital_management/reports/
   ```

2. **Open the PNG file:**
   - Double-click to view in image viewer
   - High-quality chart ready for presentations

3. **Open the CSV file:**
   - Import to Excel for further analysis
   - Create custom reports
   - Share with stakeholders

---

## ✨ Next Steps

After viewing your graphs, use the insights to:

1. **Adjust Pricing:**
   - Increase rates during peak periods
   - Offer discounts during slow periods

2. **Optimize Operations:**
   - Schedule staff based on occupancy patterns
   - Plan maintenance during low-demand periods

3. **Strategic Planning:**
   - Focus on high-performing room types
   - Target marketing for slow periods
   - Forecast future revenue

4. **Export & Share:**
   - Include charts in business reports
   - Share insights with team
   - Make data-driven decisions

---

## 🚀 Success!

You now have:
- ✅ Clean, meaningful reservation data (522 records)
- ✅ 6 months of realistic booking patterns
- ✅ Ability to generate analytics through UI
- ✅ Multiple chart types and time buckets
- ✅ Exportable data for further analysis

**Your database is ready for comprehensive business analytics!**

---

**Last Updated:** November 13, 2025  
**Data Range:** June 1 - November 30, 2025 (6 months)  
**Total Records:** 522 reservations (problematic data removed)
