__author__ = 'Ed den Beer'
'''
Created on 2 july 2014
Version 1.0 Added info

@author: Ed den Beer - Rockwell Automation
'''

import csv
import sys
import datetime

from gi.repository import Gtk

class Main():
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('glade/CopyDataToArray.glade')
        # Connect the signals/events from the glade file
        self.builder.connect_signals(self)

        #Get objects from glade file
        self.entSourceArray = self.builder.get_object('entSourceArray')
        self.entSourceStart = self.builder.get_object('entSourceStart')
        self.entDesArray = self.builder.get_object('entDesArray')
        self.entDesStart = self.builder.get_object('entDesStart')
        self.chbCSVWithSrcArray = self.builder.get_object('chbCSVWithSrcArray')
        self.chbCSVWithDesArray = self.builder.get_object('chbCSVWithDesArray')
        self.entNrOfItems = self.builder.get_object('entNrOfItems')
        self.textview1 = self.builder.get_object('textview1')
        self.cbbLanguage = self.builder.get_object('cbbLanguage')
        self.cbbDiscAna = self.builder.get_object('cbbDiscAna')
        self.cbbSrcType = self.builder.get_object('cbbSrcType')
        self.cbbDesType = self.builder.get_object('cbbDesType')
        self.statusbar = self.builder.get_object('statusbar')

         #Get the window object and show it
        self.window = self.builder.get_object("applicationwindow1")
        self.window.show_all()
        #Close main when window gets closed
        self.window.connect("destroy", Gtk.main_quit)

        #Declaration of variables
        self.SrcType = 0
        self.DesType = 0
        self.text = ''
        self.Nr_Of_Items = 0
        self.tag_src_array = ''
        self.tag_des_array = ''
        self.start_src_array = ''
        self.start_des_array = ''
        self.chbCSVWithSrcArray_active = False
        self.chbCSVWithDesArray_active = False
        self.dig_ana = ''
        self.lang = ''
        self.src_text = ''
        self.des_text = ''
        # its context_id - not shown in the UI but needed to uniquely identify
        # the source of a message
        self.context_id = self.statusbar.get_context_id("status")
        # we push a message onto the statusbar's stack
        self.statusbar.push(self.context_id, "Waiting for you to do something...")


    def on_btnQuit_clicked(self, *args):
        Gtk.main_quit(*args)

    def on_btnInfo_clicked(self, button):
        """
        Open info dialog form
        :param button:
        """
        help_text =  "\n".join(['This program can be used to generate logic to copy data from tags to an array or from an array to tags. ',
            'It is also possible to copy data from one list of tags to another. ',
            'With the check-boxes you can select if the source tags, the destination tags or both source and destination tags are in the CSV file.',
            'If you select, or the source tags or the destination tags, then the CSV file contains one column of tags',
            'If you select both check-boxes then the CSV file contains two columns of tags, the first with the source tags, the second the destination tags',
            'Under the checkboxes is the place where you can type the name and start address, and select if the array is a DINT or INT type',
            'Two languages can be selected, ladder or structured text.',
            'The last selection is analog or digital.'])
        MessageBox.info('Information:', help_text)



    def on_btnGenerate_clicked(self, button):
        if self.get_data_from_form() == 0:
                self.generate()

    def get_data_from_form(self):
        self.chbCSVWithSrcArray_active = self.chbCSVWithSrcArray.get_active()
        self.chbCSVWithDesArray_active = self.chbCSVWithDesArray.get_active()

        #If source tags in CSV file is selected get data from window
        if not self.chbCSVWithSrcArray_active:
            self.tag_src_array = self.entSourceArray.get_text()
            #Check if a array tag name is given
            if self.tag_src_array == '':
                MessageBox.error('Source array name', 'No array tag name present')
                return -1
            #Check if the value is an integer
            self.start_src_array = CheckData.int('Source array start nr', self.entSourceStart.get_text())
             #Check the response from the integer check
            if self.start_src_array == -1:
                return -1
            #Determine if DINT or INT is used
            if self.cbbSrcType.get_active_text() == 'DINT':
                self.SrcType = 31
            else:
                self.SrcType = 15

        #If destination tags in CSV file is selected get data from window
        if not self.chbCSVWithDesArray_active:
            self.tag_des_array = self.entDesArray.get_text()
            #Check if a array tag name is given
            if self.tag_des_array == '':
                MessageBox.error('Destination array name', 'No array tag name present')
                return -1
            #Check if the value is an integer
            self.start_des_array = CheckData.int('Destination array start nr', self.entDesStart.get_text())
            #Check the response from the integer check
            if self.start_des_array == -1:
                return -1
            #Determine if DINT or INT is used
            if self.cbbDesType.get_active_text() == 'DINT':
                self.DesType = 31
            else:
                self.DesType = 15

        #If source and destination are not in the CSV file then check the number of items:
        if not self.chbCSVWithSrcArray_active and not self.chbCSVWithDesArray_active:
            #Get number of items to copy
            self.Nr_Of_Items = CheckData.int('Copy length', self.entNrOfItems.get_text())
            #Check the response from the integer check
            if self.Nr_Of_Items == -1:
                return -1

        #Select ditital or analog
        self.dig_ana = self.cbbDiscAna.get_active_text()
        self.lang = self.cbbLanguage.get_active_text()

        return 0

    def generate(self):
        # self.get_button.config(state='disabled')
        self.file = ''

        #If a CSV file is used, open file dialog
        if self.chbCSVWithSrcArray_active or self.chbCSVWithDesArray_active:

            #TODO Add faulthandling
            #self.file = None
            fd = FileDialog
            fd.open_file(self)
            #Check the response of the dialog
            if fd.get_response(self) == Gtk.ResponseType.OK:
                self.statusbar.push(self.context_id, fd.get_filename(self))
            else:
                MessageBox.warning('No file is selected', 'Click Generate code again and select a CSV file.')
                self.statusbar.push(self.context_id, 'No file selected')
                return
            #TODO Add fault handling
            #Open the file in a csv reader
            f = open(fd.get_filename(self))
            del fd #delete filedialog object
            self.reader = csv.reader(f, delimiter=',')


        start = datetime.datetime.now()  #For performance testing

        #Create a textbuffer and empty textview
        self.textbuffer = self.textview1.get_buffer()
        self.textbuffer.set_text('')
        self.text = ''

        #Depending on the selection of data in de CSV file the csv is processed
        if self.chbCSVWithSrcArray_active and self.chbCSVWithDesArray_active:
            self.process_csv_2columns()
        elif self.chbCSVWithSrcArray_active and not self.chbCSVWithDesArray_active:
            self.process_csv_source_array()
        elif self.chbCSVWithDesArray_active and not self.chbCSVWithSrcArray_active:
            self.process_csv_destination_array()
        elif not self.chbCSVWithDesArray_active and not self.chbCSVWithSrcArray_active:
            self.process_no_csv()

        #self.get_button.config(state='normal')
        finish = datetime.datetime.now()
        print(finish - start)

    def process_csv_2columns(self):
        """
        Process a CSV file with 2 columns, the source and the destination array's/tags
        """
        if self.dig_ana == 'Analog':
            prefix_col_1 = 'MOV'
            prefix_col_2 = ''
        else:
            prefix_col_1 = 'XIC'
            prefix_col_2 = 'OTE'

        try:
            for row in self.reader:
                cellnr = 0
                self.text = ''
                self.src_text = ''

                if self.lang == 'Ladder':
                    for cell in row:
                        if cellnr == 0:
                            self.text = ' '.join([prefix_col_1 , str(cell)])
                        if cellnr == 1:
                            self.text = ' '.join([self.text, prefix_col_2, str(cell) , "\n"])
                        cellnr += 1
                else:  # Structured text
                    for cell in row:
                        if cellnr == 0:
                            self.src_text = ''.join([str(cell)])
                        if cellnr == 1:
                            self.text = ''.join([ self.text, str(cell), ' := ', self.src_text, "\n"])
                        cellnr += 1

                #Put row in textview
                self.textbuffer.insert(self.textbuffer.get_end_iter(), self.text)

        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (self.file, self.reader.line_num, e))

    def process_csv_source_array(self):
        """
        Process a CSV file with 1 column that contains the source array/tags
        """
        array_nr = self.start_des_array
        digit = 0

        try:
            for row in self.reader:
                cellnr = 0
                self.text = ''
                self.src_text = ''

                for cell in row:
                    if cellnr == 0:
                        if self.dig_ana == 'Analog':
                            if self.lang == 'Ladder':
                                self.text = ''.join(['MOV', ' ', str(cell), ' ', self.tag_des_array, '[', str(array_nr),']', "\n"])
                            else:
                                self.text = ''.join([self.tag_des_array, '[', str(array_nr), ']', ' := ',str(cell), "\n"])
                        else:
                            if self.lang == 'Ladder':
                                self.text = ''.join(['XIC ', str(cell), ' OTE ', self.tag_des_array, '[', str(array_nr),'].',str(digit), "\n"])
                            else:
                                self.text = ''.join([self.tag_des_array, '[', str(array_nr), '].', str(digit), ' := ', str(cell), "\n"])
                            digit += 1
                            if digit > self.DesType:
                                digit = 0
                                array_nr += 1
                    cellnr += 1

                #Put row in textview
                self.textbuffer.insert(self.textbuffer.get_end_iter(), self.text)

        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (self.file, self.reader.line_num, e))

    def process_csv_destination_array(self):
        """
        Process a CSV file with 1 column that contains the destination array/tags
        """
        array_nr = self.start_src_array
        digit = 0

        try:
            for row in self.reader:
                cellnr = 0
                self.text = ''

                for cell in row:
                    if cellnr == 0:
                        if self.dig_ana == 'Analog':
                            if self.lang == 'Ladder':
                                self.text = ''.join(['MOV', ' ', self.tag_src_array, '[', str(array_nr),']', ' ',
                                                     str(cell), "\n"])
                            else:
                                self.text = ''.join([str(cell), ' := ', self.tag_src_array, '[', str(array_nr),']',"\n"])
                        else:
                            if self.lang == 'Ladder':
                                self.text = ''.join(['XIC ', self.tag_src_array,'[', str(array_nr), '].',
                                                     str(digit), ' OTE ', str(cell), "\n"])
                            else:
                                self.text = ''.join([str(cell), ' ', self.tag_src_array,'[', str(array_nr), '].',
                                                     str(digit), "\n"])
                            digit += 1
                            if digit > self.SrcType:
                                digit = 0
                                array_nr += 1
                    cellnr += 1

                #Put row in textview
                self.textbuffer.insert(self.textbuffer.get_end_iter(), self.text)

        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (self.file, self.reader.line_num, e))

    def process_no_csv(self):
        """
        Process a CSV file with 1 column that contains the destination array/tags
        """
        scr_array_nr = self.start_src_array
        des_array_nr = self.start_des_array
        src_digit = 0
        des_digit = 0

        try:
            for index in range(self.Nr_Of_Items):
                if self.dig_ana == 'Analog':
                    if self.lang == 'Ladder':
                        self.text = ''.join(['MOV', ' ', self.tag_src_array, '[', str(scr_array_nr), ']',
                                             ' ', self.tag_des_array,'[', str(des_array_nr), ']', "\n"])
                    else:
                        self.text = ''.join([self.tag_des_array, '[', str(des_array_nr), ']', ' := ', self.tag_src_array, '[', str(scr_array_nr), ']', "\n"])

                    scr_array_nr += 1
                    des_array_nr += 1

                else:
                    if self.lang == 'Ladder':
                        self.text = ''.join(['XIC ', self.tag_src_array,'[',  str(scr_array_nr), '].',
                                            str(src_digit), ' OTE ', self.tag_des_array, '[', str(des_array_nr),'].',
                                            str(des_digit), "\n"])
                    else:
                        self.text = ''.join([self.tag_des_array, '[', str(des_array_nr),'].', str(src_digit), ' := ', self.tag_src_array, '[', str(scr_array_nr), '].', str(des_digit), "\n"])

                    #Handle the number of digits, 15 or 31
                    src_digit += 1
                    des_digit += 1
                    if src_digit > self.SrcType:
                        src_digit = 0
                        scr_array_nr += 1
                    if des_digit > self.DesType:
                        des_digit = 0
                        des_array_nr += 1

                #Put row in textview
                self.textbuffer.insert(self.textbuffer.get_end_iter(), self.text)
                self.statusbar.push(self.context_id, 'Code generated, no csv file used.')

        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (self.file, self.reader.line_num, e))

##############################################################################################################


class CheckData:
    def int(title, text):
        """
        :param title: Title of message dialog when text is no int
        :param text: The value as a string to be tested if it is an integer
        :return: -1 if test fails, text is not an integer
        """
        try:
            if int(text) >= 0:
                return int(text)
            else:
                MessageBox.error(title, 'Value ' + text + ' is less then 0')
                return -1
    
        except ValueError:
            MessageBox.error(title, 'Value ' + text + ' is not a number')
            return -1

 ###############################################################################################################


class MessageBox:
    def info(text, text2=None):
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK,
                                   text)
        if text2 is not None:
            dialog.format_secondary_text(text2)
        dialog.run()
        dialog.destroy()

    def warning(text, text2=None):
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.WARNING,
                                   Gtk.ButtonsType.OK,
                                   text)
        if text2 is not None:
            dialog.format_secondary_text(text2)
        dialog.run()
        dialog.destroy()

    def error(text, text2=None):
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK,
                                   text)
        if text2 is not None:
            dialog.format_secondary_text(text2)
        dialog.run()
        dialog.destroy()

    def question(text, text2=None):
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO,
                                   text)
        if text2 is not None:
            dialog.format_secondary_text(text2)
        response = dialog.run()
        dialog.destroy()
        return response

# #############################################################################################################


class FileDialog:
    def __init__(self):
        self.filename = None
        self.response = None

    def open_file(self):
        file_open_dialog = Gtk.FileChooserDialog(title="Open CSV file", buttons=(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        FileDialog.add_filters(file_open_dialog)

        self.response = file_open_dialog.run()

        if self.response == Gtk.ResponseType.OK:
            self.filename = file_open_dialog.get_filename()

        file_open_dialog.destroy()

    #Get filename of open file dialog
    def get_filename(self):
        return self.filename

    #Get response of open file dialog
    def get_response(self):
        return self.response

    def add_filters(dialog):
        filter_csv = Gtk.FileFilter()
        filter_csv.set_name("CSV files")
        filter_csv.add_pattern("*.csv")
        dialog.add_filter(filter_csv)

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        filter_text.add_pattern("*.txt")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)


if __name__ == '__main__':
    main = Main()
    Gtk.main()
