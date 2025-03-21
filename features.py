def toggle_autoscroll(app):
    app.autoscroll_active = not app.autoscroll_active
    if app.autoscroll_active:
        app.highlight_active = False
        app.block_active = False
        app.start_autoscroll()

def toggle_highlight(app):
    app.highlight_active = not app.highlight_active
    if app.highlight_active:
        app.autoscroll_active = False
        app.block_active = False
        app.highlight_current_line()

def toggle_block(app):
    app.block_active = not app.block_active
    if app.block_active:
        app.autoscroll_active = False
        app.highlight_active = False
        app.block_non_reading_area()
