import os
import fnmatch
import openpyxl
import datetime
import time
import sys

import_directory = "c:\wt\import\\"
export_directory = "c:\wt\\"
import_file_pattern = 'AZ_????.xlsx'
output_filename = 'wtreport.xlsx'


def prepare_export_worksbook():
    """Creates the  Export Excel Base workbook.

    This function creates the base workbook with two worksheets. and the base headers
    it uses the filenames from the modules scope .

    Args:

    Returns:

    Todo:
        Refactor to accpet arguments for finlepaths instead of using module scope vars
            """
    export_workbook = openpyxl.workbook.Workbook()
    _ = export_workbook.remove_sheet(export_workbook.active)
    line = 1
    column = 1
    worksheet = export_workbook.create_sheet("transform_input")
    worksheet.cell(line, column, "Datum")
    worksheet.cell(1, 2, "Worktime")
    worksheet.cell(1, 3, "Travel active")
    worksheet.cell(1, 4, "Travel passive")
    worksheet.cell(1, 5, "Daytype")
    worksheet.cell(1, 6, "Summe")
    worksheet.cell(1, 7, "Sollzeit")
    worksheet.cell(1, 8, "Mehrzeit")
    worksheet.cell(1, 9, "Jahr")
    worksheet.cell(1, 10, "Kalenderwoche")
    worksheet.cell(1, 11, "Wochentag")
    worksheet.cell(1, 12, "Projekt")
    # hier irgendwand format einführen

    worksheet_weeksum = export_workbook.create_sheet("week_summary")
    worksheet_weeksum.cell(1, 1, "Weekcode")
    worksheet_weeksum.cell(1, 2, "Summe AZ/W")
    worksheet_weeksum.cell(1, 3, "Summe Travel Akt/W")
    worksheet_weeksum.cell(1, 4, "Summe Travel Pas/W")
    worksheet_weeksum.cell(1, 5, "17w Average AZ")
    worksheet_weeksum.cell(1, 6, "17w Average AZ incl act")
    worksheet_weeksum.cell(1, 7, "17w Average AZ overall")

    try:
        export_workbook.save(export_directory + output_filename)
        export_workbook.close()
    except FileExistsError:
        Print(FileExistsError.with_traceback())


def Correct_worktime_vacation(import_worksheet, export_worksheet, current_importline,current_exportline):
    """Sets the working time for vacation days to 0 in the overall worksheet.

        This function replaces the 8 hours of Standard worktime with 0 to allow for correct
        average worktime calculation.

        Args:
            import_worksheet
            export_worksheet
            current_importline
            current_exportline

        Returns:

        Todo:
           implement also sick leave
                """
    #global current_importline, current_exportline
    if (str(import_worksheet.cell(current_importline, 5).value).casefold() == "urlaub"):
        export_worksheet.cell(current_exportline, 2).value = 0
    else:
        export_worksheet.cell(current_exportline, 2).value = import_worksheet.cell(current_importline, 2).value


def write_weeksummary(worksheet_weeksum,
                      current_weeksumline,
                      current_weekcode,
                      week_beginline,
                      week_endline):
    """Calculates and writes the week summary.

        This function calculates the weekly summary of work and travel hours and, if possible,
        creates the weekly value for the 17 weeks averages

        Args:
            worksheet_weeksum
            current_weeksumline
            current_weekcode
            week_beginline
            week_endline

        Returns:

        Todo:
           implement also sick leave
                    """
    worksheet_weeksum.cell(current_weeksumline, 1, current_weekcode)
    worksheet_weeksum.cell(current_weeksumline, 2,
                           "=Sum(transform_input!B" + str(week_beginline) + ":B" + str(week_endline) + ")*24")
    worksheet_weeksum.cell(current_weeksumline, 3,
                           "=Sum(transform_input!c" + str(week_beginline) + ":c" + str(
                               week_endline) + ")*24")
    worksheet_weeksum.cell(current_weeksumline, 4,
                           "=Sum(transform_input!d" + str(week_beginline) + ":d" + str(
                               week_endline) + ")*24")
    if (current_weeksumline > 17):
        worksheet_weeksum.cell(current_weeksumline, 5,
                               "=Sum(b" + str(current_weeksumline) + ":B" + str(
                                   current_weeksumline - 16) + ")/17")
        worksheet_weeksum.cell(current_weeksumline, 6,
                               "=Sum(c" + str(current_weeksumline) + ":B" + str(
                                   current_weeksumline - 16) + ")/17")
        worksheet_weeksum.cell(current_weeksumline, 7,
                               "=Sum(d" + str(current_weeksumline) + ":B" + str(
                                   current_weeksumline - 16) + ")/17")


def main():

    prepare_export_worksbook()

    export_workbook = openpyxl.open(export_directory + output_filename)
    export_worksheet = export_workbook.active
    worksheet_weeksum = export_workbook.get_sheet_by_name("week_summary")
    import_filelist = os.scandir(import_directory)
    current_exportline = 2
    current_weeksumline = 2

    current_weekcode = "empty"
    week_beginline = 2
    week_endline = 0

    for filename in import_filelist:

        if fnmatch.fnmatch(filename.name, import_file_pattern):
                print(filename.name)
                month = filename.name[5:7]
                year = "20"+filename.name[3:5]
                print(month,year)
                import_workbook = openpyxl.open(import_directory + filename.name)
                import_worksheet = import_workbook.active
                current_importline = 6


                while True:
                    import_day = import_worksheet.cell(current_importline,1).value
                    try:
                        print(import_day)
                        day=datetime.date(int(year),int(month),int(import_day))
                        print(day)
                        export_worksheet.cell(current_exportline,1,day)
                        export_worksheet.cell(current_exportline, 12, import_worksheet.cell(current_importline,5).value) # projektkommentar

                        Correct_worktime_vacation(import_worksheet,export_worksheet, current_importline,current_exportline) #AZ
                        export_worksheet.cell(current_exportline, 3, import_worksheet.cell(current_importline,3).value) #akt Travel
                        export_worksheet.cell(current_exportline, 4, import_worksheet.cell(current_importline, 4).value) # pass travel
                        export_worksheet.cell(current_exportline,6,"=Sum(B"+str(current_exportline)+":d"+str(current_exportline)+")*24") # summe
                        export_worksheet.cell(current_exportline, 9, year) # Jahr
                        export_worksheet.cell(current_exportline, 11, day.isoweekday())  # Wochentag
                        ic = day.isocalendar()
                        #print(day.timetuple()[1])
                        if ic[1]==1 and day.timetuple()[1]==12:
                            export_worksheet.cell(current_exportline, 9, str(int(year)+1))  # Jahr
                        export_worksheet.cell(current_exportline, 10, str(ic[1]))  # KW
                        weekcode = str(export_worksheet.cell(current_exportline, 9).value)+str(export_worksheet.cell(current_exportline, 10).value)
                        print(weekcode, current_weekcode)

                        if (weekcode != current_weekcode):
                            week_endline = current_exportline - 1

                            if current_weekcode == "empty":
                                current_weekcode = weekcode

                            else:
                                week_endline = current_exportline - 1
                                write_weeksummary(worksheet_weeksum, current_weeksumline,current_weekcode, week_beginline,week_endline)
                                week_beginline = current_exportline

                                current_weekcode = weekcode
                                current_weeksumline = current_weeksumline+1
                        current_importline = current_importline + 1
                        current_exportline = current_exportline + 1
                    except:
                        break

                    '''except ValueError:
                        Print(ValueError.with_traceback())
                        break
                    except TypeError:
                        Print(TypeError.with_traceback())
                        break'''

    export_workbook.save(export_directory + output_filename)




if __name__ == "__main__":
    if len(sys.argv) < 2:
        main()
    elif (len(sys.argv) == 2 ):
        main (sys.argv[1])
    elif (len(sys.argv) == 3 ):
        main(sys.argv[1],sys.argv[2])
    elif (len(sys.argv) == 4):
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    elif (len(sys.argv) == 5):
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

