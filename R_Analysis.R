setwd("C:/Users/sussery/Desktop/Python Code")
library(readxl)

df_AQUSA <-read_excel("Requirements_Quality_Scores_Baseline.xlsx", sheet = 1)

#######################BASELINE DATA ANALYSIS##################################
### Descriptive analysis for AQUSA Quality Scores###

AQUSA<-summary(df_AQUSA['Baseline_Rounded'])

# Histogram of baseline quality scores
#with(df_AQUSA, hist(Baseline_Rounded, 
#	main="Baseline Quality Scores \n
# 	(AQUSA)", 
#	xlab="Quality Score", 
#	border="black", 
#	col="blue",
#	xlim=c(0,115),
#    	breaks=seq(0,115, l=10),
#	axes = TRUE))

#axis(side=1, at=seq(0,115, 10))

#abline(v = mean(df_AQUSA$Baseline_Rounded),
# 	col = "orange",
# 	lwd = 2)

#abline(v = median(df_AQUSA$Baseline_Rounded),
# 	col = "red",
# 	lwd = 2)

#par(cex.axis=0.75)

#legend("bottomright", # location of legend within plot area
# 	c("Mean", "Median", "±2SD"),
# 	col = c("Red", "Orange", "Black"), lty = c(6, 1, 2), lwd = c(2, 1, 1),
#      xpd=TRUE, inset=c(0,1), cex=0.7, bty='n')


#Computing mean and standard deviations
#m   <- mean(df_AQUSA$Baseline_Rounded)
#std <- sd(df_AQUSA$Baseline_Rounded)
#v = m + c(0, 2*std, -2*std)

#Plotting mean and ±2SD values
#abline(v = m + c(0, 2*std, -2*std), lty=c(1,2,2))

## Hypothesis Testing - Wilcoxon Signed Rank Test###
#http://www.sthda.com/english/wiki/paired-samples-wilcoxon-test-in-r

my_data<-df_AQUSA[c(1,3)]

before <-df_AQUSA$Baseline
after <-df_AQUSA$Revised
# Create a data frame
my_data <- data.frame( 
                group = rep(c("Baseline", "Revised"), each = 832),
                weight = c(before,  after)
                )

# Plot paired data
library(PairedData)
pd <- paired(before, after)
plot(pd, type = "profile") + theme_bw()

res <- wilcox.test(weight ~ group, data = my_data, paired = TRUE)
wilcox.test(weight ~ group, data = my_data, paired = TRUE,
        alternative = "less")

#####---------------SemSim Scores--------------------###

#df_SemSim <-read_excel("sem_chart.xlsx", sheet = 1)


#with(df_SemSim , hist(semscore, 
#	main="StoryLine Cosine Similarity \n Histogram", 
#	xlab="Cosine Similarity Score", 
#	border="black", 
#	col="blue",
#	xlim=c(40,110),
#    	breaks=seq(40,125, l=100),
#	axes = TRUE))
#
#axis(side=1, at=seq(40,110, 100))

#abline(v = mean(df_SemSim$semscore),
# 	col = "orange",
# 	lwd = 2)

#abline(v = median(df_SemSim$semscore),
# 	col = "red",
# 	lwd = 2)

#par(cex.axis=0.75)

#legend("bottomright", 
#	c("Mean", "Median", "±2SD"),
# 	col = c("Red", "Orange", "Black"), 
#	lty = c(6, 1, 2), lwd = c(2, 1, 1),
#      xpd=TRUE, inset=c(0,1), 
#	cex=0.7, bty='n')

#Computing mean and standard deviations
#m <- mean(df_SemSim$semscore)
#std <- sd(df_SemSim$semscore)
#v = m + c(0, 2*std, -2*std)

#Plotting mean and ±2SD values

#abline(v = m + c(0, 2*std, -2*std), lty=c(1,2,2))
