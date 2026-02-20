import textwrap

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas


class LinkedInCarouselGenerator:
    def __init__(self, filename="carousel.pdf"):
        # LinkedIn carousel ideal size: 1080x1080 or 1080x1350 (Portrait)
        # We will use a square format for universality: 600x600 points (approx 8.3 inch square)
        self.width = 600
        self.height = 600
        self.c = canvas.Canvas(filename, pagesize=(self.width, self.height))

        # Design Constants
        self.primary_color = HexColor("#0A66C2")  # LinkedIn Blue
        self.text_color = HexColor("#000000")
        self.bg_color = HexColor("#FFFFFF")
        self.font_bold = "Helvetica-Bold"
        self.font_reg = "Helvetica"

    def create_slide(self, title, body, footer_text="Swipe ->"):
        # Background
        self.c.setFillColor(self.bg_color)
        self.c.rect(0, 0, self.width, self.height, fill=1, stroke=0)

        # Header Bar
        self.c.setFillColor(self.primary_color)
        self.c.rect(0, self.height - 80, self.width, 80, fill=1, stroke=0)

        # Logo/Brand Placeholder
        self.c.setFillColor(HexColor("#FFFFFF"))
        self.c.setFont(self.font_bold, 24)
        self.c.drawString(30, self.height - 50, "RECRUITING NEWS")

        # Title
        self.c.setFillColor(self.text_color)
        self.c.setFont(self.font_bold, 36)

        # Wrap Title
        title_lines = textwrap.wrap(title, width=20)
        y = self.height - 150
        for line in title_lines:
            self.c.drawCentredString(self.width / 2, y, line)
            y -= 45

        # Body
        self.c.setFont(self.font_reg, 24)
        body_lines = textwrap.wrap(body, width=30)
        y = y - 40  # Gap

        for line in body_lines:
            self.c.drawCentredString(self.width / 2, y, line)
            y -= 30

        # Footer
        self.c.setFillColor(self.primary_color)
        self.c.setFont(self.font_bold, 18)
        self.c.drawRightString(self.width - 30, 30, footer_text)

        # Finish Page
        self.c.showPage()

    def generate_demo(self):
        # Slide 1: Hook
        self.create_slide(
            "Wenn das Licht ausgeht...",
            "Die juristischen Probleme fangen erst an.\nKRITIS & Blackouts 2026.",
        )

        # Slide 2: Problem
        self.create_slide(
            "Die Rechtslage",
            "Haftungsketten bei Stromausfall sind unklar.\nWer zahlt, wenn die Charité dunkel bleibt?",
        )

        # Slide 3: Solution/Firm Pitch
        self.create_slide(
            "Wir lösen das.",
            "Unsere Energy-Practice berät genau an dieser Schnittstelle von Technik & Recht.",
        )

        # Slide 4: CTA
        self.create_slide(
            "Komm ins Team!",
            "Du willst strategisch denken?\nWir suchen Associates in Berlin.\n\nLink in Bio.",
            footer_text="Apply Now",
        )

        self.c.save()
        print("Carousel generated.")


if __name__ == "__main__":
    gen = LinkedInCarouselGenerator("LinkedIn_Posts/Recruiting_Carousel.pdf")
    gen.generate_demo()
