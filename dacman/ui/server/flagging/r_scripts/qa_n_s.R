##########
# TITLE: QA for DETECTING AND FLAGGING NAs, DUPLICATES, OUTLIERS AND EXTREME VALUES IN TIME SERIES
##########
ls()
rm (list = ls())

# DOWNLOAD PACKAGES  ----
library (vctrs)
library (rstatix)
library(optparse)


read_variable <- function(dataset, var_name, is_numeric=TRUE) {
    var = dataset[,var_name]
    if (is_numeric) {
        var = suppressWarnings(as.numeric(var))
    } else {
        var = suppressWarnings(as.character(var))
    }
    
    return(var)
}

format_date <- function(dataset, date_col, date_format='%m/%d/%Y %H:%M:%S') {
    Date = as.POSIXct(as.character (dataset[,date_col]), date_format, tz='')

    # Stop if class of Date is not 'POSIXct'
    stopifnot(class(Date)[1] == 'POSIXct')

    return(Date)
}

##############################################################
# DETECT AND FLAG DUPLICATED DATES AND VARIABLE VALUES ----
##############################################################

detect_na <- function(var) {
    variable.Na = ifelse(is.na(var), 1, 0)

    return(variable.Na)
}

detect_dupl <- function(var) {
    # IDENTIFY IF THERE ARE DUPLICATED DATES/TIMES (using library {vctrs} )
    #cat("Variable has duplicates: ", vec_duplicate_any(variable))
    cat(sprintf("Variable has duplicates: %s\n", vec_duplicate_any(var)))

    # CREATE A VECTOR OF FLAGS FOR DUPLICATED TIME STAMPS (FLAG ALL DUPLICATES)
    variable.dupl = vec_duplicate_detect(var) # flag all duplicates (not only starting from the 2nd duplicated value)

    variable.Dupl = ifelse(variable.dupl=="TRUE", 'DUPL', variable.dupl)

    return(variable.Dupl)
}

detect_na_dupl <- function(var) {
    # IDENTIFY IF THERE ARE DUPLICATED DATES/TIMES (using library {vctrs} )
    #cat("Variable has duplicates: ", vec_duplicate_any(variable))
    cat(sprintf("Variable has duplicates: %s\n", vec_duplicate_any(var)))

    # CREATE A VECTOR OF FLAGS FOR DUPLICATED TIME STAMPS (FLAG ALL DUPLICATES)
    variable.dupl = vec_duplicate_detect(var) # flag all duplicates (not only starting from the 2nd duplicated value)

    variable.NaDupl = ifelse(is.na(var), 1, ifelse(variable.dupl=="TRUE", 'DUPL', 0 ))

    return(variable.NaDupl)
}

detect_dupl_numeric <- function(var, n=3) {
    cat(sprintf("Numeric Variable has duplicates: %s\n", vec_duplicate_any(variable)))

    # Compute the lengths and values of runs of equal values in a vector using 'rle'--'Run Length Encoding'
    rl <- rle(variable)
    rp = rep(rl$lengths != n, times=rl$lengths)

    variable.Dupl = ifelse(rp=="TRUE", var, 'DUPL')

    return(variable.Dupl)
}

detect_na_dupl_numeric <- function(var, n=3) {
    # IDENTIFY IF THERE ARE DUPLICATED DATES/TIMES (using library {vctrs} )
    #cat("Numeric Variable has duplicates: ", vec_duplicate_any(variable))
    cat(sprintf("Numeric Variable has duplicates: %s\n", vec_duplicate_any(var)))

    # Compute the lengths and values of runs of equal values in a vector using 'rle'--'Run Length Encoding'
    rl <- rle(var)

    # FIND SUBSEQUENT DUPLICATES, IF THERE ARE AT LEAST n DUPLICATES (default -> n = 3)
    rp = ifelse (is.na(var), 'NA', rep(rl$lengths != n, times=rl$lengths))

    variable.NaDupl = ifelse (rp == 'NA', 1, ifelse(rp=="TRUE", 0, 'DUPL'))

    return(variable.NaDupl)
}

################################################
## IDENTIFY OUTLIERS AND EXTREME VALUES ----
################################################

detect_outliers <- function(var, iqr_coef=1.5) {
    # Create a vector to specify outliers, using TRUE/FALSE ----
    outl = is_outlier(as.numeric(var), coef=iqr_coef)

    # FLAGGING OF OUTLIERS ----
    Flag.outl = ifelse (outl=='TRUE', 1, 0)
    Flag.outl = ifelse (is.na(Flag.outl), 0, Flag.outl)

    return(Flag.outl)
}

detect_outliers_extremes <- function(var, outlier_iqr_coef=1.5, extreme_iqr_coef=3) {
    # Create a vector to specify outliers, using TRUE/FALSE ----
    outl = is_outlier(as.numeric(var), coef=outlier_iqr_coef)

    # Create a vector to specify extremes, using TRUE/FALSE ----
    extr = is_outlier(as.numeric(var), coef=extreme_iqr_coef)

    # FLAGGING OF OUTLIERS ----
    Flag.outl = ifelse (outl=='TRUE', 1, ifelse (extr== 'TRUE', 2, 0 ))
    Flag.outl = ifelse (is.na (Flag.outl), 0, Flag.outl )

    # FLAGGING OF EXTREMES ----
    Flag.extr = ifelse (extr=='TRUE', 1, ifelse (extr== 'TRUE', 2, 0 ))
    Flag.extr = ifelse (is.na (Flag.extr), 0, Flag.extr)

    outl_extr_list <- list(outl=Flag.outl, extr=Flag.outl)

    return(outl_extr_list)
}

##################################################
# SAVING FLAGGED RESULTS TO FILE ----
##################################################

save_file <- function(var_name, var, flag_var, flag_outl, flag_extr) {
    df <- NULL
    if (flag_var == NULL && flag_outl == NULL && flag_extr == NULL) {
        stop("Variable didn't go through any Flagging process")
    } else if (flag_var == NULL && flag_outl == NULL) {
        df = data.frame(var, flag_extr)
        names(df) <- c(
                        var_name,
                        paste("flag_extr", var_name, sep = "_")
                    )
    } else if (flag_var == NULL && flag_extr == NULL) {
        df = data.frame(var, flag_outl)
        names(df) <- c(
                        var_name,
                        paste("flag_outl", var_name, sep = "_")
                    )
    } else if (flag_outl == NULL && flag_extr == NULL) {
        df = data.frame(var, flag_var)
        names(df) <- c(
                        var_name,
                        paste("flag", var_name, sep = "_")
                    )
    } else if (flag_var == NULL) {
        df = data.frame(var, flag_outl, flag_extr)
        names(df) <- c(
                        var_name,
                        paste("flag_outl", var_name, sep = "_"),
                        paste("flag_extr", var_name, sep = "_")
                    )
    } else if (flag_outl == NULL) {
        df = data.frame(var, flag_var, flag_extr)
        names(df) <- c(
                        var_name,
                        paste("flag", var_name, sep = "_"),
                        paste("flag_extr", var_name, sep = "_")
                    )
    } else if (flag_extr == NULL) {
        df = data.frame(var, flag_var, flag_outl)
        names(df) <- c(
                        var_name,
                        paste("flag", var_name, sep = "_"),
                        paste("flag_outl", var_name, sep = "_")
                    )
    } else {
        df = data.frame(var, flag_var, flag_outl, flag_extr)
        names(df) <- c(
                        var_name,
                        paste("flag", var_name, sep = "_"),
                        paste("flag_outl", var_name, sep = "_"),
                        paste("flag_extr", var_name, sep = "_")
                    )
    }

    write.csv(df, paste(paste("QA_flagging_", var_name, sep = ""), ".csv", sep=""))
}


#####################################################################################


option_list = list(
    make_option(c("-f", "--file"), type="character", default=NULL, 
              help="dataset file name", metavar="character"),
    make_option(c("-o", "--out"), type="character", default="QA_flagging.csv",
              help="output file name [default= %default]", metavar="character"),
    make_option(c("-v", "--variable"), type="character",
              help="variables to flag", metavar="character"),
    make_option(c("--is_numeric"), action = "store_true", default = FALSE,
              help="Check if the variable has numeric values [default= %default]")
    make_option(c("--is_date"), action = "store_true", default = FALSE,
              help="Check if the variable is date [default= %default]")
    make_option(c("-n", "--check_null"), action = "store_true", default = FALSE,
              help="Check NULL values [default= %default]")
    make_option(c("-d", "--check_dupl"), action = "store_true", default = FALSE,
              help="Check duplicate values")
    make_option(c("-s", "--subsequent"), type = "integer", default = 3,
              help="Number of subsequent values to be considered duplicate",
              metavar = "number")
    make_option(c("-b", "--bad"), type="character", default=NULL, 
              help="comma separated range 'from,to'. e.g '0,100'", metavar="character")
    make_option(c("-t", "--out_iqr"), type="numeric", default=0, 
              help="IQR coefficient for outlier values detection", metavar="character")
    make_option(c("-e", "--extr_iqr"), type="numeric", default=0, 
              help="IQR coefficient for extreme values detection", metavar="character")
    #make_option(c("-v", "--variable"), type="character", default=NULL, 
    #          help="comma separated list of variables to flag", metavar="character")
)
 
opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

if (opt$file == NULL) {
    stop("An input file needs to be set")
}

if (opt$out == NULL) {
    stop("An output filename needs to be set")
}

if (opt$is_numeric == TRUE && opt$is_date == TRUE) {
    stop("Either the Numeric flag or the Date flag can be set")
}

if (opt$variable == NULL) {
    stop("A variable name needs to be specified")
}


bad_vals_range <- NULL

if (opt$bad != NULL) {
    bad_vals_range <- strsplit(opt$bad, ",")
}

#x = read.csv(file = '/project/QA_no_seasonal/AirportData_2008-2019_v3.csv')

input_file = read.csv(file=opt$file)
var_name <- opt$variable

Var <- NULL
if (opt$is_numeric) {
    Var <- read_variable(input_file, var_name)
} else if (opt$is_date) {
    Var <- format_date(input_file, var_name)
} else {
    Var <- read_variable(input_file, var_name, is_numeric=FALSE)
}

########################
# FLAGGING OF VARIABLES
########################

flag_var <- NULL

if (opt$check_null && opt&check_dupl && is_numeric) {
    flag_var <- detect_na_dupl_numeric(Var, n=opt$subsequent)
} else if (opt$check_null && opt&check_dupl) {
    flag_var <- detect_na_dupl(Var)
} else if (opt&check_dupl && is_numeric) {
    flag_var <- detect_dupl_numeric(Var, n=opt$subsequent)
} else if (opt&check_dupl) {
    flag_var <- detect_dupl(Var)
} else if (opt$check_null) {
    flag_var <- detect_na(Var)
}

Flag <- NULL
Flag.outl <- NULL
Flag.extr <- NULL

if (opt$out_iqr != 0 && opt$extr_iqr != 0) {
    Flag <- detect_outliers_extremes(
                    Var,
                    outlier_iqr_coef=opt$out_iqr,
                    extreme_iqr_coef=opt$extr_iqr
                )
    Flag.outl <- Flag$outl
    Flag.extr <- Flag$extr
} else if (opt$out_iqr != 0) {
    Flag.outl <- detect_outliers(Var, iqr_coef=opt$out_iqr)
} else if (opt$extr_iqr != 0) {
    Flag.extr <- detect_outliers(Var, iqr_coef=opt$extr_iqr)
}

save_file(var_name, Var, flag_var, Flag.outl, Flag.extr)

head (df)
summary (df)


