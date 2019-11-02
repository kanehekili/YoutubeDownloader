'''
Created on Oct 25, 2019

@author: matze
'''
import gi
import YtModel
from YtModel import Downloader
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk,GLib
import os
import threading




TARGET_ENTRY_TEXT =0
DRAG_ACTION = Gdk.DragAction.COPY
YT_PATH ="/usr/bin/youtube-dl"
TEXT_MAP = None

def _t(s):
    if not s in TEXT_MAP:
        print('TEXT_MAP["%s"]="missing"'%(s))
        return s
    return TEXT_MAP[s]


class YtWindow(Gtk.Window):
    '''
    classdocs
    '''


    def __init__(self,model):
        '''
        Constructor
        '''
        self.should_abort=False
        self.model = model

        Gtk.Window.__init__(self, title=_t("TITLE"))
        self.config=model.config
        self._initWidgets()
        self.define_url_targets()
        self.treeIter = None
        
    def _initWidgets(self):
        here = os.path.dirname(os.path.realpath(__file__))
        self.set_icon_from_file(os.path.join(here,"youtube.png"))
        self.set_default_size(self.model.getScreenX(), self.model.getScreenY())
        toolVbox = self._createToolbar()
        self.list = self._createList()
        buttonrow= self._createLowerButtonRow()
        mainbox = Gtk.VBox()
        self.add(mainbox)
     
        mainbox.pack_start(toolVbox,False,False,0)
        mainbox.pack_start(self.list,True,True,0)
        mainbox.pack_end(buttonrow,False,False,0)
  
        #self.add(mainbox)
        self.set_border_width(5)
        self.connect("delete-event", self.on_winClose, None)
        self.connect("show",self.on_Startup, None)
 
        
        self.show_all()
 
    def _createToolbar(self):
        #self.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color(6450, 000, 0000))
        self.set_position(Gtk.WindowPosition.CENTER)

        toolbar = Gtk.Toolbar()
        newtb = Gtk.ToolButton(stock_id=Gtk.STOCK_ADD) #Add manual URL
        newtb.set_tooltip_text(_t("TIP_TOOL_ADD"))
        newtb.connect("clicked",self.on_tool_add)
        opentb = Gtk.ToolButton(stock_id=Gtk.STOCK_OPEN)#Load a list
        opentb.set_tooltip_text(_t("TIP_TOOL_OPEN"))
        opentb.connect("clicked",self.on_tool_load)
        savetb = Gtk.ToolButton(stock_id=Gtk.STOCK_SAVE)#save a list
        savetb.set_tooltip_text(_t("TIP_TOOL_SAVE"))
        savetb.connect("clicked",self.on_tool_save)
        settings=Gtk.ToolButton(stock_id=Gtk.STOCK_PROPERTIES)
        settings.set_tooltip_text(_t("TIP_TOOL_SETTINGS"))
        settings.connect("clicked",self.on_tool_settings)
        dd = Gtk.ComboBoxText()
        dd.append_text(_t("COMBO_VIDEO"))
        dd.append_text(_t("COMBO_AUDIO"))
        dd.set_active(self.model.getDownloadType())
        dd.set_tooltip_text(_t("TIP_TOOL_COMBO"))
        dd.connect("changed",self.on_tool_comboChanged)
        combo = Gtk.ToolItem()
        combo.add(dd)
        
        sep = Gtk.SeparatorToolItem()
        toolbar.insert(newtb, 0)
        toolbar.insert(opentb, 1)
        toolbar.insert(savetb, 2)
        toolbar.insert(settings,3)
        toolbar.insert(sep, 4)
        toolbar.child_set(sep, expand=True);
        toolbar.insert(combo,5)


        vbox = Gtk.VBox(expand=False, spacing=2)
        vbox.pack_start(toolbar, False, False, 0)
        return vbox
    
    def _createList(self):
        self.fileStore = Gtk.ListStore(str,str,float);
        theList = Gtk.TreeView(model=self.fileStore)
        for n,name in enumerate([_t("COL1"),_t("COL2"),_t("COL3")]):
            if n is not 2:
                cell = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(name,cell,text=n);
                column.set_resizable(True)
                column.set_expand(True)
            else:
                cell = Gtk.CellRendererProgress()
                column = Gtk.TreeViewColumn(name,cell,value=n);
                column.set_alignment(0.5)
            theList.append_column(column)
        
        theList.set_tooltip_text(_t("TIP_LIST"))
        self.selection = theList.get_selection()
        self.selection.connect("changed", self.on_selected)
        swH = Gtk.ScrolledWindow()
        swH.add(theList)
        swH.connect("drag-data-received", self.on_drag_data_received)
        return swH
    
 
    def define_url_targets(self):
        self.list.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        self.list.drag_dest_set_target_list(None)
        self.list.drag_dest_add_text_targets()
        #?self.list.drag_dest_add_uri_targets() 
     
    def _createLowerButtonRow(self):
       
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        lowerBtnBox = Gtk.HBox(expand=False,spacing=3)
        self.spinner = Gtk.Spinner()
        lowerBtnBox.pack_start(self.spinner,False, False, 5)
        
        self.statusField = Gtk.Label()
        lowerBtnBox.pack_start(self.statusField,False, False, 5) 
        
        self.buttonStart = Gtk.Button(label=_t("BUTTON_OK"),image=Gtk.Image(stock=Gtk.STOCK_APPLY))
        self.buttonStart.set_tooltip_text(_t("TIP_BTN_OK"))
        self.buttonStart.connect("clicked", self.on_convert_clicked)
        lowerBtnBox.pack_end(self.buttonStart, False, False, 5)
        
        self.buttonCanx = Gtk.Button(label=_t("BUTTON_CANX"),image=Gtk.Image(stock=Gtk.STOCK_CANCEL))
        self.buttonCanx.set_tooltip_text(_t("TIP_BTN_CANX"))
        self.buttonCanx.connect("clicked", self.on_close_clicked)
        lowerBtnBox.pack_end(self.buttonCanx, False, False,5)
        
        self.buttonDel = Gtk.Button(label=_t("BUTTON_DEL"),image=Gtk.Image(stock=Gtk.STOCK_DELETE))
        self.buttonDel.set_tooltip_text(_t("TIP_BTN_DEL"))
        self.buttonDel.connect("clicked", self.on_delete_clicked)
        lowerBtnBox.pack_end(self.buttonDel, False, False,padding=5)

        self.buttonStart.set_sensitive(False)
        self.buttonDel.set_sensitive(False)
        frame.set_border_width(5)
        lowerBtnBox.set_border_width(5)
        frame.add(lowerBtnBox)
        return frame

    def showStatus(self,text):
        self.statusField.set_label(text) 
        return GLib.SOURCE_REMOVE
    
    def clearStatus(self):
        self.statusField.set_label("")
        return GLib.SOURCE_REMOVE
    
    def on_winClose(self, widget, event, data):
        geo = self.get_allocation()
        self.model.setScreenX(geo.width)
        self.model.setScreenY(geo.height)
        self.config.store()

    def on_Startup(self,widget, data):
        self.spinner.hide()        

    def on_close_clicked(self, widget):
        self.should_abort=True
        self.on_winClose(None,None,None)
        Gtk.main_quit()
        
        
    def on_convert_clicked(self, widget):
        self._longOperationStart()
        proc = YTDownloader(self)            
        w = WorkerThread(proc.processResult,proc)
        w.start() 

    def _longOperationStart(self):
        self.should_abort=False
        self.buttonStart.set_sensitive(False)
        self.buttonDel.set_sensitive(False)
        self.buttonCanx.set_sensitive(False)
        self.spinner.show()
        self.spinner.start()
        self.clearStatus()
                
    def _longOperationDone(self):
        self.spinner.stop()
        self.spinner.hide()
        self.updateDownloadButton()
        self.buttonCanx.set_sensitive(True)



    def on_drag_data_received(self, widget, drag_context, x,y, data,info, time):
        if info == TARGET_ENTRY_TEXT:
            rawURL =  data.get_data().decode("utf8")
            parseResult = YtModel.convertURL(rawURL)
            if parseResult is not None:
                    #process spawned - returns immediately
                    self.addURL(parseResult.geturl())
                    return

        self._showError(_t("NOT_AN_URL_ERROR"))
    
    def addURL(self,path):
        self._longOperationStart()
        rowData=[path,"?",0.0]
        currentIter = self.fileStore.append(rowData)
        proc = YTInfo(path,self)            
        w = WorkerThread(proc.processResult,proc)
        w.start() 
 
    def injectTitle(self,text):
        self._calculateSelection()
        self.fileStore.set_value(self.treeIter, 1, text)
        return GLib.SOURCE_REMOVE
    
    def injectStatus(self,aniter,aFloat):
        self.fileStore.set_value(aniter,2,aFloat)
        return GLib.SOURCE_REMOVE
    
    def _calculateSelection(self):
        parent = None
        n = self.fileStore.iter_n_children( parent )
        result = n and self.fileStore.iter_nth_child( parent, n - 1 )
        self.treeIter = result

    
    def on_selected(self, selection):
        model, self.treeIter = selection.get_selected()
        hasItems = len(self.fileStore) != 0
        self.buttonDel.set_sensitive(hasItems)
        self.buttonStart.set_sensitive(hasItems)

    def on_delete_clicked(self,widget):
        (model, item) = self.selection.get_selected()
        if item is not None:
            model.remove(item)
    
    def updateDownloadButton(self):
        hasItems = len(self.fileStore) != 0  
        self.buttonStart.set_sensitive(hasItems)
        
    def _showError(self,text):
        image = Gtk.Image()
        image.set_from_icon_name(Gtk.STOCK_DIALOG_WARNING, Gtk.IconSize.DIALOG)
        image.show()
        
        dialog = Gtk.MessageDialog(parent=self, flags=0,  message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,  text=_t("DIALOG_TITLE_ERROR"),image=image)
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()   
        return False   

    def on_tool_add(self,widget):
        dialog = URLDialog(self)
        response = dialog.run()
        error = False
        if response == Gtk.ResponseType.OK:
            rawURL = dialog.getInput()
            error = True
            parseResult = YtModel.convertURL(rawURL)
            if parseResult is not None:            
                self.addURL(parseResult.geturl())
                error=False
        dialog.destroy() 
        if error:
            self._showError(_t("NOT_AN_URL_ERROR"))
        
        
    def on_tool_load(self,widget):
        urls = self.model.getURLList()
        for item in urls:
            rowData=[item[0],item[1],float(item[2])]
            self.fileStore.append(rowData)
        self.showStatus(_t("LIST_LOADED"))

    def on_tool_save(self,widget):
        item = self.fileStore.get_iter_first ()
        urls =[]
        while ( item != None ):
            path = self.fileStore.get_value (item, 0)
            title = self.fileStore.get_value (item, 1)
            mode = self.fileStore.get_value (item, 2)
            urls.append([path,title,str(mode)])
            item = self.fileStore.iter_next(item)
        self.model.setURLList(urls)
        self.showStatus(_t("LIST_SAVED"))

    def on_tool_comboChanged(self,widget):
        self.model.setDownloadType(widget.get_active())
        #0==Video, 1== Audio
    
    def on_tool_settings(self,widget):
        dialog = SettingsDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            v= dialog.getVideoPath()
            a= dialog.getAudioPath()
            self.model.setVideoPath(v)
            self.model.setMusicPath(a)
        dialog.destroy() 

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, _t("SETTINGS_DLG"), parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.parent = parent
        self.set_default_response(Gtk.ResponseType.OK)
        x=parent.model.getScreenX()/2
        y=parent.model.getScreenY()/6
        self.set_default_size(x, y)
        self._initWidgets()
        
    def _initWidgets(self):
        text = _t("SETTINGS_LABEL")
        grpLabel= Gtk.Label()
        grpLabel.set_markup("<b>%s</b>"%text)
        grpLabel.set_justify(Gtk.Justification.FILL)
        headBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        headBox.pack_start(grpLabel, True, True,5)
        gtkdummyBox = Gtk.VBox()
        videoBox = Gtk.HBox()
        audioBox = Gtk.HBox()
        gtkdummyBox.pack_start(videoBox,True,True,5)
        gtkdummyBox.pack_start(audioBox,True,True,5)
        
        self.ventry = Gtk.Entry()
        self.ventry.set_text(self.parent.model.getVideoPath())
        fc = Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_DIRECTORY))
        fc.connect("clicked",self._onVideoChanged)
        videoBox.pack_start(self.ventry,True,True,5)
        videoBox.pack_end(fc,False,False,5)

        self.aentry = Gtk.Entry()
        self.aentry.set_text(self.parent.model.getMusicPath())
        fc = Gtk.Button(image=Gtk.Image(stock=Gtk.STOCK_DIRECTORY))
        fc.connect("clicked",self._onAudioChanged)
        audioBox.pack_start(self.aentry,True,True,5)
        audioBox.pack_end(fc,False,False,5)

        box = self.get_content_area()
        box.set_border_width(15)
        box.add(headBox)
        box.add(gtkdummyBox)
        #box.add(audioBox)
        self.show_all()
        
    def  _onVideoChanged(self,widget):
        dialog = Gtk.FileChooserDialog(title=_t("FOLDER_VIDEO_SAVE"), parent=self,action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog.set_filename(self.parent.model.getVideoPath())
        response = dialog.run()
        thePath = None
        if response == Gtk.ResponseType.OK:
            thePath = dialog.get_filename()
            self.ventry.set_text(thePath)
        dialog.destroy()

    def  _onAudioChanged(self,widget):
        dialog = Gtk.FileChooserDialog(title=_t("FOLDER_AUDIO_SAVE"), parent=self,action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog.set_filename(self.parent.model.getMusicPath())
        response = dialog.run()
        thePath = None
        if response == Gtk.ResponseType.OK:
            thePath = dialog.get_filename()
            self.aentry.set_text(thePath)
        dialog.destroy() 

    def getVideoPath(self):
        return self.ventry.get_text()
    
    def getAudioPath(self):
        return self.aentry.get_text()

class URLDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, _t("URL_DLG"), parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        x=parent.model.getScreenX()/3
        y=parent.model.getScreenY()/8
        self.set_default_size(x, y)
        self._initWidgets()
               
    def _initWidgets(self):
        text = _t("ENTER_URL")
        grpLabel= Gtk.Label()
        grpLabel.set_markup("<b>%s</b>"%text)
        grpLabel.set_justify(Gtk.Justification.FILL)
        headBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        headBox.pack_start(grpLabel, True, True,5)
        
        self.entry = Gtk.Entry()
        headBox.pack_start(self.entry,True,True,5)
        
        box = self.get_content_area()
        box.add(headBox)
        #box.add(srcBox)
        #box.add(destBox)
        self.show_all()
        
    def getInput(self):
        return self.entry.get_text()            
        
class WorkerThread(threading.Thread):
    def __init__(self, callback,processor):
        threading.Thread.__init__(self)
        self.callback = callback
        self.processor = processor

    def run(self):
        res = self.processor.run()
        # The callback runs a GUI task, so wrap it!
        GLib.idle_add(self.callback,res)

class YTDownloader():
    def __init__(self,ytWin):
        self.parent=ytWin
        self.current=None
        
    def run(self):
        fs=self.parent.fileStore
        aiter = fs.get_iter_first ()
        mode = self.parent.model.getDownloadType()
        if mode==YtModel.MODE_AUDIO:
            targetDir = self.parent.model.getMusicPath()
        else:
            targetDir = self.parent.model.getVideoPath()
        
        downloader = Downloader(self)
        while ( aiter != None ):
            self.current=aiter
            url = fs.get_value (aiter, 0)
            downloader.download(url, mode, targetDir)
            aiter = fs.iter_next(aiter)
        return "" #No error
    
    def onProgress(self,progress,size,speed):
        if self.current is not None:
            self._broadcastData(progress, speed) 

    def onProgressDone(self,fulltext):
        if self.current is not None:
            self._broadcastData(100.0, fulltext)       

    def _broadcastData(self,progress,speed):
        GLib.idle_add(self.parent.injectStatus,self.current,progress)
        GLib.idle_add(self.parent.showStatus,speed)
        
    def processResult(self,res):
        self.parent._longOperationDone()
        return GLib.SOURCE_REMOVE

class YTInfo():
    def __init__(self,url,ytWin):
        self.target=url
        self.parent=ytWin
        
    def run(self):
        res = YtModel.getInfo(self.target)
        return res
    
    def processResult(self,res):
        self.parent._longOperationDone()
        if res is not None:
            title = res["title"]
            if title is None:
                self._handleError(res)
            self.parent.injectTitle(title)
        return GLib.SOURCE_REMOVE
    
    def _handleError(self,result):
        self.parent._showError(result)
    
def start():
    model = YtModel.Model()
    global TEXT_MAP
    TEXT_MAP = model.text
    win = YtWindow(model)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
 
if __name__ == '__main__':
    start()
    pass 