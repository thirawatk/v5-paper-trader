#!/usr/bin/env python3
"""Generate a PDF from the DeepSeek-V4-Pro analysis markdown."""

from fpdf import FPDF
import textwrap

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    @staticmethod
    def sanitize(text):
        """Replace Unicode chars outside Latin-1 range with ASCII equivalents."""
        return (text
                .replace('\u2014', '--')
                .replace('\u2013', '-')
                .replace('\u2018', "'")
                .replace('\u2019', "'")
                .replace('\u201c', '"')
                .replace('\u201d', '"')
                .replace('\u2022', '*')
                .replace('\u2026', '...')
                .replace('\u2010', '-')
                )

    def c(self, text):
        """Sanitized cell."""
        return self.cell(0, 6, self.sanitize(text), align="C")

    def m(self, text, **kwargs):
        """Sanitized multi_cell."""
        return self.multi_cell(0, 5.5, self.sanitize(text), **kwargs)

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.c("Multi-Model Comparison -- US Small/Mid-Cap Growth Picks")
        self.ln(4)
        self.set_font("Helvetica", "", 8)
        self.c("DeepSeek-V4-Pro Analysis (Leg 4 of 4)")
        self.ln(8)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def heading(self, text, level=1):
        self.ln(4)
        self.set_font("Helvetica", "B", 14 if level == 1 else 12 if level == 2 else 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 7, text)
        self.ln(2)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        for item in items:
            self.multi_cell(0, 5.5, self.sanitize(f"  * {item}"))
            self.ln(0.5)

    def table(self, headers, rows, col_widths=None):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(40, 40, 40)
        self.set_text_color(255, 255, 255)

        if col_widths is None:
            total = 190
            col_widths = [total // len(headers)] * len(headers)

        # Header row
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()

        # Data rows
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        fill = False
        for row in rows:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6.5, str(cell), border=1, fill=fill, align="C")
            self.ln()
            fill = not fill
        self.ln(4)

    def section_rule(self):
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)


def generate():
    pdf = PDF()
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 10, "DeepSeek-V4-Pro Analysis", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, "US Small/Mid-Cap Growth Picks -- Leg 4 of 4", ln=True, align="C")
    pdf.ln(5)
    pdf.set_draw_color(60, 60, 60)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)

    # 1. Portfolio Thesis Assessment
    pdf.heading("1. Portfolio Thesis Assessment")
    pdf.body(
        "Verdict: The thesis is sound but structurally fragile.\n\n"
        "The portfolio is a pure-play AI infrastructure and application bet. That's not a "
        "diversification strategy -- it's a conviction trade disguised as a portfolio. "
        "DeepSeek does not mince words: if AI capex decelerates meaningfully in 2027-2028, "
        "every name in this basket gets hit simultaneously. There is no hedge.\n\n"
        "DeepSeek would add one position outside the AI value chain -- specifically a "
        "healthcare AI or industrial AI name with low correlation to hyperscaler capex cycles. "
        "The portfolio as constructed has a correlation coefficient approaching 0.85+ across "
        "all five names, which is unacceptable for a 10-year hold."
    )
    pdf.section_rule()

    # 2. Stock-by-Stock Analysis
    pdf.heading("2. Stock-by-Stock Analysis")

    # NET
    pdf.heading("NET (Cloudflare) -- HOLD / BUY on dip to ~$80", level=2)
    pdf.bullet([
        "Revenue multiple: ~50-60x forward revenue. Expensive, but defensible given 119% NRR and AI inference/edge compute monetization path.",
        "DeepSeek's concern: Cloudflare's AI story is still narrative, not revenue. Workers AI, inference at the edge -- these are TAM expansion stories, not current cash flows.",
        "First-principles DCF: At 30% revenue growth declining to 18% terminal, 25% operating margin target, and 9% WACC, intrinsic value is ~$95-105. Current price is fair-to-slightly-rich.",
        "Recommendation: 20% allocation maximum. Set a buy trigger at $80 (15% below current). Do not chase."
    ])
    pdf.ln(3)

    # S
    pdf.heading("S (SentinelOne) -- BUY, but position-size carefully", level=2)
    pdf.bullet([
        "Revenue multiple: ~15x forward revenue post-FY26E. Cheapest name in the portfolio on a relative basis.",
        "DeepSeek's view: Sentinel's AI-native security platform is genuinely differentiated. Purple AI, Storyline, AI-powered threat hunting -- these represent a fundamental shift in SOC economics.",
        "Margin of safety: At $70-75, the stock trades at ~12-13x FY26E revenue with 40%+ gross margins expanding.",
        "Recommendation: 20% allocation. Entry band $68-75. Fair value target 18-month: $105-115."
    ])
    pdf.ln(3)

    # AXON
    pdf.heading("AXON (Axon Enterprise) -- CAUTION / SMALL POSITION", level=2)
    pdf.bullet([
        "Revenue growth: 23% CAGR is real, driven by recurring ARR (cloud storage, Axon Evidence).",
        "Valuation problem: 61x forward P/E is indefensible in any value-conscious framework. "
        "Axon is a great business at 35x P/E. At 61x, you're paying for perfection.",
        "DeepSeek's hard cap: 5% of portfolio. A 'conviction but not at this price' name.",
        "Recommendation: 5-10% max. Entry band $265-280. Do NOT add at $300+."
    ])
    pdf.ln(3)

    # ON
    pdf.heading("ON Semiconductor -- BUY with scaling plan", level=2)
    pdf.bullet([
        "Structural thesis: AI inference requires enormous silicon. ON is supply-constrained, not demand-constrained.",
        "DeepSeek's math: Automotive and industrial end-markets are cyclical, but data center/AI "
        "inference demand is secular. Revenue mix is shifting toward higher-margin AI-adjacent products.",
        "Risk: Tariff escalation. ON has significant fab capacity in the US (Gresham, Oregon).",
        "Recommendation: 10% allocation. Enter at $75-80, scale in at $65-70. Stop accumulating above $90."
    ])
    pdf.ln(3)

    # FORM
    pdf.heading("FORM (Teradyne/Ultra) -- DROP", level=2)
    pdf.bullet([
        "YTD +122%: This is not discovery, this is momentum. The probe card TAM is real, but "
        "FORM is pricing in 5+ years of growth.",
        "DeepSeek's test: At current valuation, FORM needs to grow EPS 25%+ annually for 5 years.",
        "Recommendation: 0%. Sell if held. Reallocate to LSCC or cash reserve."
    ])
    pdf.ln(3)

    # LSCC
    pdf.heading("LSCC (Lam Research) -- BUY", level=2)
    pdf.bullet([
        "Better FORM: Same semiconductor equipment exposure, more diversified (etch, deposition, CVD), "
        "larger revenue base, more reasonable multiple.",
        "AI capex beneficiary: Every AI chip needs to be fabricated. Lam touches every leading-edge node.",
        "DeepSeek's valuation: ~18x forward earnings with 25%+ growth = PEG < 1. Buy signal.",
        "Recommendation: 10% allocation. Entry band $800-850."
    ])
    pdf.ln(3)

    # NVTS
    pdf.heading("NVTS (Navitas Semiconductor) -- WATCHLIST, DO NOT BUY", level=2)
    pdf.bullet([
        "GaN market is real but Navitas is priced for 50%+ market share capture that hasn't materialized.",
        "Revenue is sub-$500M. Competitive moat vs. GaN Systems, Infineon, Wolfspeed is thin.",
        "Recommendation: Watch only. Not actionable at current valuation."
    ])
    pdf.section_rule()

    # 3. Portfolio Allocation
    pdf.heading("3. DeepSeek's Revised Portfolio Allocation")

    headers = ["Rank", "Ticker", "Allocation", "Trigger Price", "Notes"]
    rows = [
        ["1", "NET", "25%", "Buy below $80", "AI inference thesis"],
        ["2", "S", "20%", "$68-75", "Best risk/reward"],
        ["3", "ON", "10%", "Scale in $65-80", "Structural supply thesis"],
        ["4", "LSCC", "10%", "Entry $800-850", "Better semi-equipment play"],
        ["5", "AXON", "5%", "Only if sub-$280", "Great biz, terrible price"],
        ["6", "Cash", "10%", "-", "Dry powder for volatility"],
        ["7", "TBD", "10%", "TBD", "Non-AI diversifier (mandatory)"],
    ]
    pdf.table(headers, rows, col_widths=[15, 28, 30, 55, 62])

    pdf.body(
        "\nKey differences from Ring's allocation:\n"
        "  - Lower AXON (5% vs 10%) -- DeepSeek is harder on valuation\n"
        "  - Higher cash reserve (10% vs 5%) -- DeepSeek assumes more volatility\n"
        "  - NVTS explicitly rejected, not just deferred\n"
        "  - Non-AI diversifier is mandatory, not optional"
    )
    pdf.section_rule()

    # 4. Stress-Test Scenarios
    pdf.heading("4. Stress-Test Scenarios")

    pdf.heading("Scenario A: Hyperscaler Capex Cut 20%", level=2)
    pdf.bullet([
        "NET: -25-30% (AI inference monetization delayed)",
        "S: -10-15% (security spend is more defensive)",
        "ON: -15-20% (semi capex cycle sensitivity)",
        "LSCC: -20-25% (same as ON, correlated)",
        "AXON: -5-10% (less correlated, law enforcement budgets sticky)",
        "Portfolio drawdown: ~15-18%"
    ])
    pdf.ln(2)

    pdf.heading("Scenario B: Tariff Escalation + Rate Hold", level=2)
    pdf.bullet([
        "ON: Most exposed (supply chain disruption, even with US fabs)",
        "LSCC: Moderate (equipment shipping costs)",
        "NET/S/AXON: Minimal direct impact, but multiple compression from rate uncertainty",
        "Portfolio drawdown: ~10-12%"
    ])
    pdf.ln(2)

    pdf.heading("Scenario C: AI Hype Deflation (2024-25 Repeat)", level=2)
    pdf.bullet([
        "All names draw down 30-40%",
        "Cash reserve becomes critical -- THIS is the scenario it exists for",
        "Non-AI diversifier would provide ballast",
        "Portfolio drawdown: ~30-35% without hedge; ~25% with non-AI position"
    ])
    pdf.section_rule()

    # 5. Summary Comparison Table
    pdf.heading("5. Four-Model Summary Comparison")

    headers2 = ["Aspect", "OWL", "Cohere", "Ring", "DeepSeek"]
    rows2 = [
        ["Stock picks", "Solid", "Sharper", "Same + questions", "Same + first-principles"],
        ["Allocation", "Weak", "Better", "Best (adds cash)", "Hardest on valuation + max cash"],
        ["Risk analysis", "Acknowledged", "Mentioned", "Stress-tested", "Quantitative scenarios"],
        ["Val. discipline", "Contradictory", "Correct but soft", "Hard caps", "Hardest, PEG-based"],
        ["Diversification", "Acknowledged", "Acknowledged", "Flagged as SPOF", "Mandatory non-AI"],
        ["Score", "B-", "B+", "A-", "B+ (portfolio C+)"]
    ]
    pdf.table(headers2, rows2, col_widths=[45, 42, 42, 42, 29])

    pdf.section_rule()

    # 6. Final Takeaway
    pdf.heading("6. DeepSeek's Honest Takeaway")
    pdf.body(
        "This portfolio is a bet that AI infrastructure spending compounds at 25%+ "
        "for a decade. That's a generational bet -- the kind of bet that makes you rich "
        "if you're right and destroys capital if you're wrong.\n\n"
        "The OWL analysis was competent but naive. Cohere improved it. Ring added "
        "discipline. But none of the three models adequately answered the question: "
        "WHAT IF YOU'RE WRONG ABOUT THE DURATION OF THE AI CAPEX CYCLE?\n\n"
        "The 10% cash reserve is smart. The non-AI diversifier is mandatory. And no "
        "name should be above 25% in a portfolio with this level of sector concentration.\n\n"
        "Final score: B+ for stock selection, C+ for risk management, D for "
        "diversification. Fix the D first."
    )

    output_path = "/root/.hermes/profiles/buddy/cache/documents/deepseek_v4pro_us_small_midcap_analysis.pdf"
    pdf.output(output_path)
    print(f"PDF written to {output_path}")


if __name__ == "__main__":
    generate()