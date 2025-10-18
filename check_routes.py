from main import app

with app.app_context():
    print('Registered routes containing "shift":')
    for rule in app.url_map.iter_rules():
        if 'shift' in rule.rule.lower():
            print(f'  {rule.endpoint}: {rule.rule}')
