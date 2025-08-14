import json

input_file = "barbearia_db.json"
output_file = "barbearia_db_identado.json"

try:
    with open(input_file, "r") as f:
        data = json.load(f)

    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Arquivo '{input_file}' formatado e salvo como '{output_file}'.")

except FileNotFoundError:
    print(f"Erro: O arquivo '{input_file}' não foi encontrado.")
except json.JSONDecodeError:
    print(f"Erro: O arquivo '{input_file}' não é um JSON válido.")