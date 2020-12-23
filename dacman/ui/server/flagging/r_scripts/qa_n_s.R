##########
# TITLE: QA for DETECTING AND FLAGGING NAs, DUPLICATES, OUTLIERS AND EXTREME VALUES IN TIME SERIES
##########
ls()
rm (list = ls())

# DOWNLOAD PACKAGES  ----
#library (zoo)
#library (plyr)
library (vctrs)
library (rstatix)
#library (DescTools)
library(optparse)


option_list = list(
    make_option(c("-f", "--file"), type="character", default=NULL, 
              help="dataset file name", metavar="character"),
    make_option(c("-o", "--out"), type="character", default="QA_flagging.csv",
              help="output file name [default= %default]", metavar="character"),
    make_option(c("-v", "--variable"), type="character", default=NULL, 
              help="comma separated list of variables to flag", metavar="character")
)
 
opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

var_list <- strsplit(opt$variable, ",")

x = read.csv(file = '/project/QA_no_seasonal/AirportData_2008-2019_v3.csv')

format_date <- function(dataset, date_col, date_format="%m/%d/%Y %H:%M:%S") {
    Date = as.POSIXct (as.character (dataset[,date_col]), date_format, tz = '')

    # Stop if class of Date is not "POSIXct"
    stopifnot(class(Date)[1] == "POSIXct")

    return(Date)
}

date_col_name <- "datetime"

Date <- format_date(x, date_col_name)

########################
# FLAGGING OF VARIABLES
########################

get_variable_list <- function(dataset, var_name) {
    var = dataset[,var_name]
    var= suppressWarnings(as.numeric(var))

    return(var)
}

var_col_name <- "TEMP_F"

var <- get_variable_list(x, var_col_name)

##############################################################
# DETECT AND FLAG DUPLICATED DATES AND VARIABLE VALUES ----
##############################################################
detect_na_dupl <- function(variable) {
    # IDENTIFY IF THERE ARE DUPLICATED DATES/TIMES (using library {vctrs} )
    #cat("Variable has duplicates: ", vec_duplicate_any(variable))
    cat(sprintf("Variable has duplicates: %s\n", vec_duplicate_any(variable)))

    # CREATE A VECTOR OF FLAGS FOR DUPLICATED TIME STAMPS (FLAG ALL DUPLICATES)
    variable.dupl = vec_duplicate_detect(variable) # flag all duplicates (not only starting from the 2nd duplicated value)

    variable.NaDupl = ifelse (is.na (variable), 1, ifelse(variable.dupl=="TRUE", 'DUPL', 0 ))

    return(variable.NaDupl)
}

Flag.Date.NaDupl <- detect_na_dupl(Date)

detect_na_dupl_numeric <- function(variable, n=3) {
    # IDENTIFY IF THERE ARE DUPLICATED DATES/TIMES (using library {vctrs} )
    #cat("Numeric Variable has duplicates: ", vec_duplicate_any(variable))
    cat(sprintf("Numeric Variable has duplicates: %s\n", vec_duplicate_any(variable)))

    # Compute the lengths and values of runs of equal values in a vector using 'rle'--'Run Length Encoding'
    rl <- rle(variable)

    # FIND SUBSEQUENT DUPLICATES, IF THERE ARE AT LEAST n DUPLICATES (default -> n = 3)
    rp =ifelse (is.na(variable), 'NA', rep(rl$lengths != n, times = rl$lengths))

    variable.NaDupl = ifelse (rp == 'NA', 1, ifelse(rp=="TRUE", 0, 'DUPL'))

    return(variable.NaDupl)
}

Flag.var.NaDupl <- detect_na_dupl_numeric(var)

################################################
## IDENTIFY OUTLIERS AND EXTREME VALUES ----
################################################

get_outliers_extremes <- function(variable, out_coef=1.5) {
    # Create a vector to specify outliers, using TRUE/FALSE ----
    outl = is_outlier(as.numeric (variable),  out_coef=coefficient)

    # Create a vector to specify extremes, using TRUE/FALSE ----
    extr =  is_extreme(as.numeric (variable))

    # Print a summary of the number of outliers and extremes ----
    summary (cbind(outl, extr))

    # FLAGGING OF OUTLIERS ----
    Flag.outl = ifelse (outl=='TRUE', 1, ifelse (extr== 'TRUE', 2, 0 ))
    Flag.outl = ifelse (is.na (Flag.outl), 0, Flag.outl )

    # FLAGGING OF EXTREMES ----
    Flag.extr = ifelse (extr=='TRUE', 1, ifelse (extr== 'TRUE', 2, 0 ))
    Flag.extr = ifelse (is.na (Flag.extr), 0, Flag.extr)

    Flag.outl = ifelse (is.na (Flag.outl), 0, Flag.outl)
    Flag.extr = ifelse (is.na (Flag.extr), 0, Flag.extr)

    outl_extr_list <- list(outl=Flag.outl, extr=Flag.outl)

    return(outl_extr_list)
}

Flag <- get_outliers_extremes(var)

##################################################
# SAVING FLAGGED RESULTS TO FILE ----
##################################################

# Create a data frame of Dates, variable and flags ----
df = data.frame (Date, 'Temp'=var, flag_Date=Flag.Date.NaDupl,
                 flag_var=Flag.var.NaDupl , flag_outl=as.character(Flag$outl),
                 flag_extr=as.character(Flag$extr))
head (df)
summary (df)

var.name = 'Temp'

write.csv(df, paste ('QA_flagging_no_seasonal', var.name,'.csv'))
