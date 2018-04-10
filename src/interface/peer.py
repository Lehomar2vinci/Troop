from __future__ import absolute_import

try:
    import Tkinter as Tk
except ImportError:
    import tkinter as Tk
    
from ..config import *
import colorsys

def rgb2hex(*rgb): 
    r = int(max(0, min(rgb[0], 255)))
    g = int(max(0, min(rgb[1], 255)))
    b = int(max(0, min(rgb[2], 255)))
    return "#{0:02x}{1:02x}{2:02x}".format(r, g, b)

def hex2rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i+2], 16) for i in range(0,6,2) )

def avg_colour(col1, col2, weight=0.5):
    rgb1 = hex2rgb(col1)
    rgb2 = hex2rgb(col2)
    avg_rgb = tuple(rgb1[i] * (1-weight) + rgb2[i] * weight for i in range(3))
    return rgb2hex(*avg_rgb)

def int2rgb(i):
    h = (((i + 2) * 70) % 255) / 255.0
    return [int(n * 255) for n in colorsys.hsv_to_rgb(h, 1, 1)]

def PeerFormatting(index):
    i = index % len(COLOURS["Peers"])
    c = COLOURS["Peers"][i]
    return c, "Black"

class PeerColourTest:
    def __init__(self):
        self.root=Tk.Tk()
        num = 20
        h = 30
        w = 100
        self.canvas =Tk.Canvas(self.root, width=300, height=num*h)
        self.canvas.pack()
        m = 0
        for n in range(num):
            rgb = int2rgb(n)
            m = 0
            self.canvas.create_rectangle(m * w, n * h, (m + 1) * w,  (n + 1) * h, fill=rgb2hex(*rgb))
            m = 1
            rgb = tuple(n - 30 for n in rgb)
            self.canvas.create_rectangle(m * w, n * h, (m + 1) * w,  (n + 1) * h, fill=rgb2hex(*rgb))
            m = 2
            self.canvas.create_rectangle(m * w, n * h, (m + 1) * w,  (n + 1) * h, fill="Black")
        self.root.mainloop()

class Highlight:
    def __init__(self, text, tag):
        self.text = text
        self.tag  = tag
        self.deactivate()
    def __repr__(self):
        return "<Selection: {} - {}>".format(self.start, self.end)

    def __len__(self):
        return (self.end - self.start)
    
    def set(self, start, end):
        """ Set a relative index """
        self.anchor = start
        self.start  = min(start, end)
        self.end    = max(start, end)
        self.active = True
    
    def add(self, start, end):
        """ Add a Tk index """
        self.multiple.append((start, end))
        return 
    
    def update(self, old, new):
        if new > self.anchor:
            self.start = self.anchor
            self.end   = new
        elif new < self.anchor:
            self.start = new
            self.end = self.anchor
        else:
            self.hide()
        return
    
    def deactivate(self):
        self.start    = 0
        self.end      = 0
        self.anchor   = 0
        self.active   = False
        self.multiple = []
    
    def shift(self, loc, amount):
        if self.active:
            if loc < self.start:
                self.start += amount
                self.end   += amount
            elif loc < self.end:
                self.end += amount
        return
    
    def show(self):
        """ Adds the highlight tag to the text """
        if len(self.multiple) > 0:
            for start, end in self.multiple:
                self.text.tag_add(self.tag, start, end)
        else:
            self.text.tag_add(self.tag, self.text.number_index_to_tcl(self.start), self.text.number_index_to_tcl(self.end))
        self.active = True
        return
    
    def hide(self):
        """ Removes the highlight tag from the text """
        self.clear()
        self.deactivate()
        return

    def clear(self):
        self.text.tag_remove(self.tag, "1.0", Tk.END)

class Peer:
    """ Class representing the connected performers within the Tk Widget
    """
    def __init__(self, id_num, name, widget, row=1, col=0):
        self.id = id_num
        self.root = widget # Text
        self.root_parent = widget.root

        self.name = Tk.StringVar()
        self.name.set(name)

        self.update_colours()
        
        self.label = Tk.Label(self.root,
                           textvariable=self.name,
                           bg=self.bg,
                           fg=self.fg,
                           font="Font")

        self.raised = False

        self.insert = Tk.Label(self.root,
                            bg=self.bg,
                            fg=self.fg,
                            bd=0,
                            height=2,
                            text="", font="Font" )

        self.text_tag = self.get_text_tag(self.id)
        self.code_tag = self.get_code_tag(self.id)
        self.sel_tag  = self.get_select_tag(self.id)
        self.str_tag  = self.get_string_tag(self.id)
        self.mark     = self.get_mark_tag(self.id)

        # For refreshing the text
        self.hl_eval    = Highlight(self.root, self.code_tag)
        self.hl_select  = Highlight(self.root, self.sel_tag)

        self.root.peer_tags.append(self.text_tag)

        # Stat graph

        self.count = 0
        self.graph = None

        self.configure_tags()
        
        # Tracks a peer's selection amount and location
        self.row = row
        self.col = col
        self.index_num = 0
        self.sel_start = "0.0"
        self.sel_end   = "0.0"

        # self.move(1,0) # create the peer

    def __str__(self):
        return str(self.name.get())

    @staticmethod
    def get_text_tag(p_id):
        return "text_{}".format(p_id)

    @staticmethod
    def get_code_tag(p_id):
        return "code_{}".format(p_id)

    @staticmethod
    def get_select_tag(p_id):
        return "sel_{}".format(p_id)

    @staticmethod
    def get_string_tag(p_id):
        return "str_{}".format(p_id)

    @staticmethod
    def get_mark_tag(p_id):
        return "mark_{}".format(p_id)

    def get_peer_formatting(self, index):

        fg, bg = PeerFormatting(index)

        if self.root.merge_colour is not None:
            
            w = self.root.get_peer_colour_merge_weight()

            fg = avg_colour(fg, self.root.merge_colour, w)

        return fg, bg

    def update_colours(self):
        self.bg, self.fg = self.get_peer_formatting(self.id)
        return self.bg, self.fg

    def configure_tags(self):
        doing = True
        while doing:
            try:
                # Text tags
                self.root.tag_config(self.text_tag, foreground=self.bg)
                self.root.tag_config(self.str_tag,  foreground=self.fg)
                self.root.tag_config(self.code_tag, background=self.bg, foreground=self.fg)
                self.root.tag_config(self.sel_tag,  background=self.bg, foreground=self.fg)
                # Label
                self.label.config(bg=self.bg, fg=self.fg)
                self.insert.config(bg=self.bg, fg=self.fg)
                doing = False
            except TclError:
                pass
        return

    def shift(self, amount):
        """ Updates the peer's location relative to its current location by calling `move` """
        return self.move(self.index_num + amount)

    def select_shift(self, loc, amount):
        return self.hl_select.shift(loc, amount)

    def find_overlapping_peers(self):
        """ Returns True if this peer overlaps another peer's label """

        for peer in self.root.peers.values():

            # If the indices are in overlapping position, on the same row, and the other peer is not already raised

            if peer != self:

                peer_index = peer.get_index_num()
                this_index = self.get_index_num()

                if (peer_index >= this_index) and (peer_index - this_index < len(str(self))):

                    if not peer.raised and self.is_on_same_row(peer):

                        self.raised = True

                        break

        else:

            self.raised = False

        return self.raised

    def is_on_same_row(self, other):
        """ Returns true if this peer and other peer have the first same value for their tcl index """
        return self.get_row() == other.get_row()
        
    def move(self, loc, raised = False):
        """ Updates the location of the Peer's label """

        try:

            document_length = len(self.root.read())

            # Make sure the location is valid

            if loc < 0:

                self.index_num = 0

            elif loc > document_length:

                self.index_num = document_length

            else:

                self.index_num = loc

            # Work with tcl indexing e.g. "1.0"
            
            index = self.root.number_index_to_tcl(loc)

            row, col = [int(val) for val in index.split(".")]

            self.row = row
            self.col = col

            index = "{}.{}".format(self.row, self.col)

            # Find out if this needs to be raised

            raised = self.find_overlapping_peers()

            # Update the Tk text tag

            self.root.mark_set(self.mark, index)

            # Only move the cursor if we have a valid index

            bbox = self.root.bbox(index)

            if bbox is None and self == self.root.marker:

                # If this is the local peer, make sure it is seen          

                self.root.see(self.mark) 

                # Try again to get the bounding box

                bbox = self.root.bbox(index)

            if bbox is not None:

                x, y, width, height = bbox

                x_val = x - 2

                # Label can go on top of the cursor

                if raised:

                    y_val = (y - height, y - height)

                else:

                    y_val = (y + height, y)
                
                self.label.place(x=x_val, y=y_val[0], anchor="nw")
                self.insert.place(x=x_val, y=y_val[1], anchor="nw")

            else:

                # If we're not meant to see the peer, hide it
                
                self.label.place(x=-100, y=-100)
                self.insert.place(x=-100, y=-100)


        except Tk.TclError as e:

            print(e)
            
        return self.index_num

    def select(self, start, end):
        """ Updates the selected text area for a peer """

        if start == end == 0: # start and end of 0 is a de-select

            self.hl_select.hide()

        elif self.hl_select.active:

            self.hl_select.update(start, end)

        else:

            self.hl_select.set(start, end)

        return

    def select_set(self, start, end):
        """ Override a selection area instead of incrementing """

        if start == end == 0: # start and end of 0 is a de-select

            self.hl_select.hide()

        self.hl_select.set(start, end)

        return

    def select_start(self):
        """ Returns the index of the start of the selection """
        return self.hl_select.start

    def select_end(self):
        """ Returns the index of the end of the selection """
        return self.hl_select.end

    def selection_size(self):
        return len(self.hl_select)

    def de_select(self):
        """ Remove (not delete) the selection from the text """
        if self.hl_select.active:
            self.hl_select.hide()
            return True
        else:
            return False

    def remove(self):
        """ Destroys the Tk items associated with this peer and deletes it from the address book """
        self.hl_select.hide()
        self.label.destroy()
        self.insert.destroy()
        self.root.root.graphs.delete(self.graph)
        del self.root.peers[self.id]
        return self
    
    def has_selection(self):
        """ Returns True if this peer is selecting any text """
        return self.hl_select.active

    def __highlight_select(self):
        """ Adds background highlighting to text being selected by this peer """
        self.hl_select.clear()
        if self.hl_select.start != self.hl_select.end:
            self.hl_select.show()
        return


    def highlight(self, start_line, end_line):
        """ Highlights (and schedules de-highlight) of block of text. Returns contents
            as a string """

        code = []

        if start_line == end_line: 
            end_line += 1

        for line in range(start_line, end_line):
            
            start = "%d.0" % line
            end   = "%d.end" % line

            # Highlight text only to last character, not whole line

            self.hl_eval.add(start, end)

            code.append(self.root.get(start, end))

        self.__highlight_block()
            
        # Unhighlight the line of text

        self.root.master.after(200, self.__unhighlight_block)

        return "\n".join(code)

    def __highlight_block(self):
        """ Adds background highlighting for code being evaluated"""
        self.hl_eval.show()
        return

    def __unhighlight_block(self):
        """ Removes highlight formatting from evaluated text """
        self.hl_eval.hide()
        return

    def refresh_highlight(self):
        """ If the text is refreshed while code is being evaluated, re-apply it"""
        if self.hl_eval.active:
            self.__highlight_block()
        if self.hl_select.active:
            self.__highlight_select()
        return

    def refresh(self):
        """ Don't move the marker but redraw it """
        return self.shift(0)

    def get_tcl_index(self):
        """ Returns the index number as a Tkinter index e.g. "1.0" """
        return self.root.number_index_to_tcl(self.index_num)

    def get_row(self):
        return int(self.get_tcl_index().split(".")[0])

    def get_col(self):
        return int(self.get_tcl_index().split(".")[1])

    def get_index_num(self):
        """ Returns the index (a single integer) of this peer """
        return self.index_num
    
    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id
