from http.server import BaseHTTPRequestHandler
import json
import random
import datetime
import cairosvg # Para converter SVG -> PNG
from io import BytesIO # Para trabalhar com arquivos em memória
from PIL import Image # Para combinar as imagens

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # --- LÓGICA DE SELEÇÃO DA CITAÇÃO (sem alterações) ---
        with open('quotes.json', 'r', encoding='utf-8') as f:
            quotes_data = json.load(f)
        
        # (A lógica de peso/bônus continua aqui, se desejar)
        weights = [1.0] * len(quotes_data) 
        selected_quote_obj = random.choices(quotes_data, weights=weights, k=1)[0]
        quote_text = selected_quote_obj['text']
        quote_author = selected_quote_obj['author']

        # --- NOVA LÓGICA DE IMAGEM (MAIS SIMPLES) ---

        # 1. Carregar a imagem de fundo com Pillow
        # Certifique-se que o nome do arquivo está correto.
        try:
            background = Image.open('Zoltar_Filipeta.jpg') 
        except FileNotFoundError:
            self.send_error(500, "Imagem de fundo 'Zoltar_Filipeta.jpg' não encontrada.")
            return

        image_width, image_height = background.size

        # 2. Gerar o SVG apenas com o texto rotacionado
        rotation_angle = -11.3
        text_center_x = 324
        text_center_y = 426

        text_svg_template = f"""
        <svg width="{image_width}" height="{image_height}" xmlns="http://www.w3.org/2000/svg">
            <style>
                .quote-text {{ font-family: 'Times New Roman', serif; font-size: 24px; fill: #000; text-anchor: middle; }}
                .quote-author {{ font-family: 'Times New Roman', serif; font-size: 18px; fill: #000; text-anchor: middle; }}
            </style>
            <g transform="rotate({rotation_angle}, {text_center_x}, {text_center_y})">
                <text x="{text_center_x}" y="{text_center_y - 20}" class="quote-text">{quote_text}</text>
                <text x="{text_center_x}" y="{text_center_y + 20}" class="quote-author">- {quote_author}</text>
            </g>
        </svg>
        """

        # 3. Converter o SVG do texto para um PNG transparente EM MEMÓRIA
        # CairoSVG faz isso diretamente, sem precisar de programas externos.
        # A ausência de 'background_color' já o torna transparente.
        text_overlay_png_bytes = cairosvg.svg2png(
            bytestring=text_svg_template.encode('utf-8'),
            output_width=image_width,
            output_height=image_height
        )
        
        # Abrir a imagem do texto recém-criada com Pillow
        text_overlay = Image.open(BytesIO(text_overlay_png_bytes))

        # 4. Combinar o fundo com o texto usando Pillow
        # Convertemos o fundo para RGBA para permitir a colagem com transparência.
        background = background.convert("RGBA")
        combined_image = Image.alpha_composite(background, text_overlay)
        
        # 5. Salvar a imagem final em um buffer de bytes e enviar
        img_buffer = BytesIO()
        combined_image.save(img_buffer, format="PNG")
        png_output = img_buffer.getvalue()

        # --- ENVIO DA RESPOSTA (sem alterações) ---
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(png_output)
        return