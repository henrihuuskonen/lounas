import app

def print_cli(name, func):
    data = func()
    print(name)
    if data:
        for line in data:
            print(f"    {line}")
    else:
        print("None")
    print()

print_cli("Min", app.get_min)
print_cli("Hiili", app.get_hiili)
print_cli("Silta", app.crawl_silta)
print_cli("Oikeus", app.crawl_oikeus)
print_cli("Factory", app.crawl_factory)
print_cli("Hima & Sali", app.crawl_himasali)
print_cli("Dylan Milk", app.crawl_dylanmilk)
