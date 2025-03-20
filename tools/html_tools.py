from langchain_core.tools import tool

@tool
def html_template(title: str, body: str, style: str, script: str) -> str:
    """
    Returns a simple HTML template with a title and body.
    Args:
        title (str): The title of the HTML document.
        body (str): The body content of the HTML document.
        style (str): The CSS styles to be applied to the HTML document.
        script (str): The script tags and everything inside of the script to be included in the HTML document.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    </head>
    <style>
        {style}
    </style>
    {script}
    <body>
        {body}
    </body>
    </html>
    """


@tool
def javascript_list_to_html() -> str:
    """
    Returns a simple javascript function that generates a <ul> with all of the <li> items in a list.
    """
    return """
    <script>
        function listItems(list) {
            var html = "<ul class="list-group list-group-flush">";
            for (var i = 0; i < list.length; i++) {
                html += "<li class='list-group-item'>" + list[i] + "</li>";
            }
            html += "</ul>";
            return html;
        }
    </script>
    """

@tool
def document_card(title: str, content: str, button: str) -> str:
    """
    Returns a card HTML div in bootstrap
    Args:
        title (str): The title of the card.
        content (str): The content of the card.
        button (str): The button HTML div to be included in the card.
    """
    return f"""
    <div class="card" style="width: 18rem;">
        <div class="card-body">
            <h5 class="card-title">{title}</h5>
            <p class="card-text">{content}</p>
            {button}
        </div>
    </div>
    """

@tool
def button(id: str, text: str, type: str = "primary") -> str:
    """
    Returns a button HTML div in bootstrap
    Args:
        id (str): The id of the button.
        text (str): The text to be displayed on the button.
        type (str): The type of the button. Default is "primary". Options are "primary", "secondary", "success", "danger", "warning", "info", "light", "dark".
    """
    return f"""
    <button type="button" id="{id}" class="btn btn-{type}">{text}</button>
    """

@tool
def search_bar(button: str, input_id: str, placeholder: str = "Search...", ) -> str:
    """
    Returns a search bar HTML div in bootstrap style.

    Args:
        button (str): The button HTML div to be included in the search bar.
        input_id (str): The id of the search input.
        placeholder (str): The placeholder text for the search input.

    Returns:
        str: HTML div for a search bar.
    """

    return f"""
    <div class="input-group mb-3">
        <input type="text" id="{input_id}" class="form-control" placeholder="{placeholder}" aria-label="Search"
            aria-describedby="button-addon2">
        {button}
    </div>
    """