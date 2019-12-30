setwd("C:/Users/ussery.sabrina/Desktop/Python Code")
library(readxl)

df_AQUSA <-read_excel("Requirements_Quality_Scores_Baseline_11272019.xlsx", sheet = 1)

#######################BASELINE DATA ANALYSIS##################################
### Descriptive analysis for AQUSA Quality Scores###

before<-df_AQUSA$Baseline_Rounded
after<-df_AQUSA$Revised_Rounded
diff<-df_AQUSA$diff


my_data <- data.frame( 
                group = rep(c("Baseline", "Revised"), each = 832),
                score = c(before,  after)
                )



#checking assumptions of t-test, as per: https://www.datascienceblog.net/post/statistical_test/signed_wilcox_rank_test/
#http://www.sthda.com/english/wiki/paired-samples-t-test-in-r

#install.packages("ggpubr")
library("ggpubr")
ggboxplot(my_data, x = "group", y = "score", 
          color = "group", palette = c("#00AFBB", "#E7B800"),
          order = c("Baseline", "Revised"),
          ylab = "Score", xlab = "Groups")

install.packages("PairedData")
#Plot paired data:
# Subset weight data before treatment
before <- subset(my_data,  group == "Baseline", score,
                 drop = TRUE)
# subset weight data after treatment
after <- subset(my_data,  group == "Revised", score,
                 drop = TRUE)
# Plot paired data
library(PairedData)
pd <- paired(before, after)
plot(pd, type = "profile") + theme_bw()

shapiro.test(diff)
ggplot(diff.df, aes(x = diff)) + geom_histogram()

library("car")
qqPlot(df_AQUSA$diff)


#--------------------------------------------------------------------------------------------
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

wilcox.text(before, after, paired=TRUE


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