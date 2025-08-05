import json
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Load JSON
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Jinja2 environment setup
env = Environment(
    block_start_string=r'\BLOCK{',
    block_end_string='}',
    variable_start_string=r'\VAR{',
    variable_end_string='}',
    comment_start_string=r'\#{',
    comment_end_string='}',
    trim_blocks=True,
    autoescape=False,
    loader=FileSystemLoader(".")
)

# Load LaTeX template
template = env.get_template("journal_template.tex")

# Render LaTeX with JSON data
rendered_tex = template.render(**data)

# Save rendered LaTeX
tex_file = Path("output.tex")
tex_file.write_text(rendered_tex, encoding="utf-8")

# Compile to PDF
subprocess.run(["pdflatex", "-interaction=nonstopmode", str(tex_file)], check=True)

print("✅ PDF generated successfully: output.pdf")
