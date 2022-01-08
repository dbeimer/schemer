import gi
from gi.repository import Gtk,Gdk
from gi.repository import Handy as hdy
import process_file

gi.require_version("Gtk","3.0")
gi.require_version("Handy","1")


hdy.init()
gtk_settings=Gtk.Settings.get_default ()
gtk_settings.props.gtk_application_prefer_dark_theme=True
# print(dir(gtk_settings.props))

css_provider =Gtk.CssProvider()
css_provider.load_from_path("style.css")
Gtk.StyleContext.add_provider_for_screen (Gdk.Screen.get_default (), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

DRAG_ACTION = Gdk.DragAction.COPY
TARGET_ENTRY_TEXT=0
FILE="Welcome to your fist app!!"
HEADER=None

class MainWindow(hdy.Window):

    def __init__(self):
        super().__init__()

        self.props.default_height=300
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
        # self.iconview.drag_source_set_target_list(None)

        self.drop_area.drag_dest_add_text_targets()
        # self.iconview.drag_source_add_text_targets()

class DropArea(Gtk.Label):
    def __init__(self):
        Gtk.Label.__init__(self)
        self.set_label("Drop something on me!")
        self.set_selectable(True)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        

        self.connect("drag-data-received", self.on_drag_data_received)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        # print(info)
        if info == TARGET_ENTRY_TEXT:
            text = data.get_text()
            print(widget)
            ruta=text[7:]
            print("Received text: %s" % text)
            print("File to process: %s" % ruta)
            FILE=ruta.split('/')[-1]
            
            text=process_file.process_file(ruta.strip())
            self.set_label(text)

        # elif info == TARGET_ENTRY_PIXBUF:
        #     pixbuf = data.get_pixbuf()
        #     width = pixbuf.get_width()
        #     height = pixbuf.get_height()

        #     print("Received pixbuf with width %spx and height %spx" % (width, height))  

main_window=MainWindow()
main_window.show_all()
main_window.connect("destroy", Gtk.main_quit)
Gtk.main()
