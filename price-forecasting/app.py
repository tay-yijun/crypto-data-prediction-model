from make_model import main

def handler(event, context):
    main()
    return "Model run complete"