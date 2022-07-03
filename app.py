
import gi
gi.require_version('Gtk', '3.0')
gi.require_version("Handy","1")

from gi.repository import Gtk,Gdk
from gi.repository import Handy as hdy
import process_file
from urllib.parse import urlparse,unquote



hdy.init()
gtk_settings=Gtk.Settings.get_default ()
gtk_settings.props.gtk_application_prefer_dark_theme=True
# print(dir(gtk_settings.props))

css_provider =Gtk.CssProvider()
css_provider.load_from_path("style.css")
Gtk.StyleContext.add_provider_for_screen (Gdk.Screen.get_default (), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

TARGET_ENTRY_TEXT=0
FILE="Welcome to batch helper!!"
HEADER=None

class MainWindow(hdy.Window):

    def __init__(self):
        super().__init__()

        self.props.default_height=600
        self.props.default_width=400

        HEADER=hdy.HeaderBar(show_close_button=True,title=FILE)
        header_context=HEADER.get_style_context()
        header_context.add_class("default-decoration")
        header_context.add_class(Gtk.STYLE_CLASS_FLAT)
        vbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,expand=False)
        vbox.add(HEADER)
        scrolled = Gtk.ScrolledWindow(expand=True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.drop_area=DropArea()

        scrolled.add(self.drop_area)
        vbox.add(scrolled)
        self.add(vbox)
        self.add_text_targets()

    def add_text_targets(self, button=None):
        self.drop_area.drag_dest_set_target_list(None)
        self.drop_area.drag_dest_add_text_targets()

        # self.iconview.drag_source_add_text_targets()
        # self.iconview.drag_source_set_target_list(None)

class DropArea(Gtk.TextView):
    def __init__(self):
        Gtk.Label.__init__(self)
        textBuffer=self.get_buffer()
        styleContext=self.get_style_context()
        styleContext.add_class("text-area")
        textBuffer.set_text("Drop something on me!")

        # self.set_editable(False)
        self.set_margin_left(10)
        self.set_margin_right(10)
        self.set_margin_bottom(10)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("drag-motion", self.on_drag_motion)

    def on_drag_motion(self, widget, drag_context, x, y, time):
        self.set_editable(True)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        if info == TARGET_ENTRY_TEXT:

            text = data.get_text()
            url_obj = urlparse(text)
            file_path=unquote(url_obj.path)

            textBuffer=self.get_buffer()
            textBuffer.set_text("Procesing file...")

            text=process_file.process_file(file_path.strip())

            textBuffer.set_text(text)
            self.set_editable(False)

main_window=MainWindow()
main_window.show_all()
main_window.connect("destroy", Gtk.main_quit)
Gtk.main()
