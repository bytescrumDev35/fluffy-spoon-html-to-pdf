2#!/usr/bin/env python3
"""
HTML to PDF Converter - Static HTML Import and PDF Generation
A utility to convert static HTML files or HTML strings to PDF documents
"""

import os
import sys
import argparse
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PDF generation imports
try:
    from weasyprint import HTML, CSS
    PDF_GENERATION_AVAILABLE = True
    PDF_METHOD = "weasyprint"
    logger.info("Using WeasyPrint for PDF generation")
except ImportError:
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas
        PDF_GENERATION_AVAILABLE = True
        PDF_METHOD = "reportlab"
        logger.info("Using ReportLab for PDF generation")
    except ImportError:
        PDF_GENERATION_AVAILABLE = False
        PDF_METHOD = None
        logger.error(
            "No PDF generation library available. Install weasyprint or reportlab.")


class HTMLToPDFConverter:
    """Convert HTML files or strings to PDF documents"""

    def __init__(self, output_directory: str = "./pdf_outputs"):
        self.output_directory = output_directory
        self.ensure_output_directory()

    def ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        os.makedirs(self.output_directory, exist_ok=True)
        logger.info(f"Output directory: {self.output_directory}")

    def convert_html_file_to_pdf(self, html_file_path: str, output_pdf_path: Optional[str] = None) -> str:
        """
        Convert an HTML file to PDF

        Args:
            html_file_path: Path to the HTML file
            output_pdf_path: Optional output PDF path. If None, auto-generated.

        Returns:
            Path to the generated PDF file
        """
        if not PDF_GENERATION_AVAILABLE:
            raise RuntimeError(
                "PDF generation not available. Install weasyprint or reportlab.")

        # Check if HTML file exists
        if not os.path.exists(html_file_path):
            raise FileNotFoundError(f"HTML file not found: {html_file_path}")

        # Generate output path if not provided
        if output_pdf_path is None:
            html_filename = Path(html_file_path).stem
            output_pdf_path = os.path.join(
                self.output_directory, f"{html_filename}.pdf")

        logger.info(f"Converting HTML file: {html_file_path}")
        logger.info(f"Output PDF: {output_pdf_path}")

        try:
            if PDF_METHOD == "weasyprint":
                return self._convert_with_weasyprint_file(html_file_path, output_pdf_path)
            elif PDF_METHOD == "reportlab":
                return self._convert_with_reportlab_file(html_file_path, output_pdf_path)
            else:
                raise RuntimeError(f"Unknown PDF method: {PDF_METHOD}")
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise

    def convert_html_string_to_pdf(self, html_content: str, output_pdf_path: str) -> str:
        """
        Convert HTML string content to PDF

        Args:
            html_content: HTML content as string
            output_pdf_path: Output PDF file path

        Returns:
            Path to the generated PDF file
        """
        if not PDF_GENERATION_AVAILABLE:
            raise RuntimeError(
                "PDF generation not available. Install weasyprint or reportlab.")

        logger.info(
            f"Converting HTML content ({len(html_content)} characters)")
        logger.info(f"Output PDF: {output_pdf_path}")

        try:
            if PDF_METHOD == "weasyprint":
                return self._convert_with_weasyprint_string(html_content, output_pdf_path)
            elif PDF_METHOD == "reportlab":
                return self._convert_with_reportlab_string(html_content, output_pdf_path)
            else:
                raise RuntimeError(f"Unknown PDF method: {PDF_METHOD}")
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise

    def _convert_with_weasyprint_file(self, html_file_path: str, output_pdf_path: str) -> str:
        """Convert HTML file to PDF using WeasyPrint"""
        if PDF_METHOD != "weasyprint":
            raise RuntimeError("WeasyPrint not available")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

        # Convert using WeasyPrint
        HTML(filename=html_file_path).write_pdf(output_pdf_path)

        logger.info(
            f"✅ PDF generated successfully using WeasyPrint: {output_pdf_path}")
        return output_pdf_path

    def _convert_with_weasyprint_string(self, html_content: str, output_pdf_path: str) -> str:
        """Convert HTML string to PDF using WeasyPrint"""
        if PDF_METHOD != "weasyprint":
            raise RuntimeError("WeasyPrint not available")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

        # Convert using WeasyPrint
        HTML(string=html_content).write_pdf(output_pdf_path)

        logger.info(
            f"✅ PDF generated successfully using WeasyPrint: {output_pdf_path}")
        return output_pdf_path

    def _convert_with_reportlab_file(self, html_file_path: str, output_pdf_path: str) -> str:
        """Convert HTML file to PDF using ReportLab (basic conversion)"""
        # Read HTML content
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        return self._convert_with_reportlab_string(html_content, output_pdf_path)

    def _convert_with_reportlab_string(self, html_content: str, output_pdf_path: str) -> str:
        """Convert HTML string to PDF using ReportLab (basic conversion)"""
        try:
            from bs4 import BeautifulSoup
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.pagesizes import letter
        except ImportError as e:
            raise RuntimeError(
                f"Required libraries not available for ReportLab conversion: {e}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

        # Parse HTML to extract text content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text_content = soup.get_text()

        # Create PDF using ReportLab
        doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title if available
        title_tag = soup.find('title')
        if title_tag:
            story.append(Paragraph(title_tag.get_text(), styles['Title']))
            story.append(Spacer(1, 12))

        # Split content into paragraphs and add to story
        paragraphs = text_content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), styles['Normal']))
                story.append(Spacer(1, 6))

        # Build PDF
        doc.build(story)

        logger.info(
            f"✅ PDF generated successfully using ReportLab: {output_pdf_path}")
        return output_pdf_path

    def batch_convert_html_files(self, html_directory: str, output_directory: Optional[str] = None) -> Dict[str, str]:
        """
        Convert multiple HTML files in a directory to PDFs

        Args:
            html_directory: Directory containing HTML files
            output_directory: Optional output directory for PDFs

        Returns:
            Dictionary mapping HTML file paths to PDF file paths
        """
        if output_directory is None:
            output_directory = self.output_directory

        if not os.path.exists(html_directory):
            raise FileNotFoundError(
                f"HTML directory not found: {html_directory}")

        html_files = [f for f in os.listdir(
            html_directory) if f.lower().endswith('.html')]

        if not html_files:
            logger.warning(f"No HTML files found in {html_directory}")
            return {}

        logger.info(f"Found {len(html_files)} HTML files to convert")

        results = {}
        for html_file in html_files:
            html_path = os.path.join(html_directory, html_file)
            pdf_filename = f"{Path(html_file).stem}.pdf"
            pdf_path = os.path.join(output_directory, pdf_filename)

            try:
                converted_path = self.convert_html_file_to_pdf(
                    html_path, pdf_path)
                results[html_path] = converted_path
                logger.info(f"✅ Converted: {html_file} -> {pdf_filename}")
            except Exception as e:
                logger.error(f"❌ Failed to convert {html_file}: {e}")
                results[html_path] = f"Error: {str(e)}"

        return results


def create_sample_html_file(filename: str = "sample_report.html") -> str:
    """Create a sample HTML file for testing"""
    sample_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Website Audit Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f9f9f9;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .score {
            background: linear-gradient(45deg, #3498db, #2ecc71);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
        }
        .score h3 {
            margin: 0;
            font-size: 2em;
        }
        .metric {
            display: inline-block;
            background: #ecf0f1;
            padding: 15px;
            margin: 10px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .metric strong {
            color: #2c3e50;
        }
        .recommendations {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #e74c3c;
        }
        .recommendations ul {
            margin: 10px 0;
        }
        .recommendations li {
            margin-bottom: 8px;
        }
        @media print {
            body { background: white; }
            .container { box-shadow: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Website Audit Report</h1>
        <p><strong>URL:</strong> https://example.com</p>
        <p><strong>Generated:</strong> July 30, 2025</p>
        
        <div class="score">
            <h3>Overall Score: 85/100</h3>
            <p>Good performance with room for improvement</p>
        </div>
        
        <h2>Performance Metrics</h2>
        <div>
            <div class="metric">
                <strong>First Contentful Paint:</strong> 1.2s
            </div>
            <div class="metric">
                <strong>Largest Contentful Paint:</strong> 2.1s
            </div>
            <div class="metric">
                <strong>Cumulative Layout Shift:</strong> 0.05
            </div>
            <div class="metric">
                <strong>First Input Delay:</strong> 45ms
            </div>
        </div>
        
        <h2>SEO Analysis</h2>
        <ul>
            <li>✅ Title tag present and optimized</li>
            <li>✅ Meta description found</li>
            <li>⚠️ Missing alt text on 3 images</li>
            <li>✅ Proper heading structure (H1-H6)</li>
            <li>✅ Mobile-friendly design</li>
        </ul>
        
        <h2>Security Assessment</h2>
        <ul>
            <li>✅ HTTPS encryption enabled</li>
            <li>✅ Security headers present</li>
            <li>⚠️ Mixed content warnings detected</li>
            <li>✅ No malware detected</li>
        </ul>
        
        <h2>Accessibility Score: 78/100</h2>
        <ul>
            <li>✅ Proper color contrast ratios</li>
            <li>⚠️ Some form elements missing labels</li>
            <li>✅ Keyboard navigation supported</li>
            <li>⚠️ Missing skip navigation links</li>
        </ul>
        
        <div class="recommendations">
            <h2>Priority Recommendations</h2>
            <ul>
                <li>Add alt text to all images for better accessibility and SEO</li>
                <li>Optimize images to reduce load times</li>
                <li>Fix mixed content warnings by ensuring all resources use HTTPS</li>
                <li>Add proper labels to form elements</li>
                <li>Implement skip navigation links for better accessibility</li>
                <li>Consider implementing a Content Security Policy</li>
            </ul>
        </div>
        
        <h2>Conversion Optimization</h2>
        <ul>
            <li>✅ Clear call-to-action buttons</li>
            <li>✅ Contact information easily accessible</li>
            <li>⚠️ Forms could be simplified</li>
            <li>✅ Trust signals present (testimonials, certifications)</li>
        </ul>
        
        <p style="text-align: center; margin-top: 40px; color: #7f8c8d;">
            <em>Report generated by Website Auditor Pro</em>
        </p>
    </div>
</body>
</html>"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(sample_html)

    logger.info(f"✅ Sample HTML file created: {filename}")
    return filename


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Convert HTML files to PDF')
    parser.add_argument('--html', type=str,
                        help='Path to HTML file to convert')
    parser.add_argument('--output', type=str, help='Output PDF file path')
    parser.add_argument(
        '--batch', type=str, help='Directory containing HTML files for batch conversion')
    parser.add_argument('--output-dir', type=str,
                        default='./pdf_outputs', help='Output directory for PDFs')
    parser.add_argument('--create-sample', action='store_true',
                        help='Create a sample HTML file for testing')

    args = parser.parse_args()

    # Initialize converter
    converter = HTMLToPDFConverter(output_directory=args.output_dir)

    if args.create_sample:
        # Create sample HTML file
        sample_file = create_sample_html_file("sample_report.html")
        print(f"📄 Sample HTML file created: {sample_file}")

        # Convert sample to PDF
        try:
            pdf_path = converter.convert_html_file_to_pdf(sample_file)
            print(f"🎉 Sample PDF generated: {pdf_path}")
        except Exception as e:
            print(f"❌ Failed to generate sample PDF: {e}")

    elif args.html:
        # Convert single HTML file
        try:
            pdf_path = converter.convert_html_file_to_pdf(
                args.html, args.output)
            print(f"🎉 PDF generated successfully: {pdf_path}")
        except Exception as e:
            print(f"❌ Conversion failed: {e}")

    elif args.batch:
        # Batch convert HTML files
        try:
            results = converter.batch_convert_html_files(
                args.batch, args.output_dir)

            success_count = sum(1 for v in results.values()
                                if not v.startswith("Error:"))
            total_count = len(results)

            print(
                f"🎉 Batch conversion completed: {success_count}/{total_count} files converted successfully")

            for html_path, pdf_path in results.items():
                if pdf_path.startswith("Error:"):
                    print(f"❌ {os.path.basename(html_path)}: {pdf_path}")
                else:
                    print(
                        f"✅ {os.path.basename(html_path)} -> {os.path.basename(pdf_path)}")

        except Exception as e:
            print(f"❌ Batch conversion failed: {e}")
    else:
        print("No action specified. Use --help for usage information.")
        print("\nQuick start:")
        print("1. Create a sample: python html_to_pdf_converter.py --create-sample")
        print("2. Convert HTML file: python html_to_pdf_converter.py --html sample_report.html")
        print(
            "3. Batch convert: python html_to_pdf_converter.py --batch /path/to/html/files")


if __name__ == "__main__":
    main()
