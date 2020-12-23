ls()
rm (list = ls())

library (rstatix)


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

################################################
## Plotting Temperature with outliers + extremes
################################################

plot_variable <- function(date, var, var_name) {
    # Values above Q3 + 1.5xIQR or below Q1 - 1.5xIQR are considered as outliers.
    # Values above Q3 + 3xIQR or below Q1 - 3xIQR are considered as extreme points (or extreme outliers).

    ## Determine upper and lower outliers using library {rstatix} ----

    # Compute the Interquartile Range of the var values.
    iqr = IQR(na.omit(var))

    # Compute Q1 (p = 25%) and Q3 (p = 75%)
    (q = quantile(var, na.rm=T, c(0.25, 0.75) ))

    # Compute max and min of outliers ----
    (outl.mx = as.numeric (q[2]) + 1.5*iqr)
    (outl.mn = as.numeric (q[1]) - 1.5*iqr)

    # Compute max and min of extreme values ----
    (extr.mx = as.numeric (q[2]) + 3*iqr)
    (extr.mn = as.numeric (q[1]) - 3*iqr)

    # Create a data frame of outliers ----
    id.outl = identify_outliers (data.frame (seq(1, length (var)),  var), var)

    # Give column names of the data frame of outliers ----
    colnames(id.outl)= c('ID', 'var', 'outlier', 'extreme')
    id.outl

    # PLOT THE TIME SERIES OF THE VARIABLE ----
    plot (date, var, t='l', xlab = '', ylab = '', ylim = c(extr.mn,extr.mx) ); grid ()

    # PLOT THE HORIZONTAL LINES OF OUTLIERS ----
    abline (h =c(outl.mx,outl.mn), col = 3)

    # PLOT THE HORIZONTAL LINES OF EXTREMES ----
    abline (h =c(extr.mx,extr.mn), col = 2)

    # PLOT THE POINTS OUTLIERS ----
    points (date[id.outl$ID], var[id.outl$ID] , pch =16, col =3, cex =1)
    # points (Date[id.outl$ID], var [id.outl$ID] , pch =16, col =3, cex =1)

    # Label the outlier and extreme lines ----
    text (date[round (length(date)/2)], (outl.mn-1) , 'lower outliers', cex = 0.75, col =3)
    text (date[round (length(date)/2)], (outl.mx+1) , 'upper outliers', cex = 0.75, col =3)

    text (date[round (length(date)/2)], (extr.mn-1) , 'lower extreme', cex = 0.75, col =2)
    text (date[round (length(date)/2)], (extr.mx+1) , 'upper extreme', cex = 0.75, col =2)

    # Title and a legend of the figure ----
    title (main = var_name, ylab = var_name)
    legend ('topright', c('Outliers', 'Extreme'), pch = 16, col = c(3,2), cex = 0.75)
}

plot_variable(Date, var, "Temperature")

delete_duplicated <- function(variable) {
    # DELETE ROWS WITH NAs
    variable = variable[complete.cases(variable)] # it leaves only the rows with no NAs
    variable = variable[!duplicated(variable)]

    return(variable)
}

Date <- delete_duplicated(Date)

get_interval_diff <- function(variable) {
    diff = as.numeric(diff(variable)) # If var is Time, diff is in seconds

    return(diff)
}

diff.Date <- get_interval_diff(Date)

##########
# Plott and CHECK THE TIME INTERVALS ----
##########

plot_time_intervals <- function(date, diff_date) {
    # PLOT THE TIME SERIES OF TIME INTERVALS ----
    plot (date[1:length(diff_date) ] , diff_date, log ='y', t = 'b', ylab = 'Time intervals, hrs', xlab = '')
    title ('Time intervals')
    grid ()
}

plot_time_intervals(Date, diff.Date)

##################################################
# Plott and CHECK THE DENSITY FUNCTION ----
##################################################

plot_time_interval_density <- function(diff_date) {
    # PLOT THE DENSITY FUNCTION OF TIME INTERVALS ----
    plot (density (diff_date), t = 'b', log = 'xy', xlab = 'Time intervals, hours', main = 'Density plot of time intervals')
    grid ()
}

plot_time_interval_density(diff.Date)
