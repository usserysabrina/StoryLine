## Purpose is to determine relationship between user story quality and writing style
# reference: https://stats.idre.ucla.edu/r/dae/multinomial-logistic-regression/

library(readxl)
df_ANOVA <-read_excel("writing style regression.xlsx", sheet = 1)
df_ANOVA[is.na(df_ANOVA)] <- " "
df_ANOVA$rho_conc <- as.numeric(as.character(df_ANOVA$rho_conc))
df_ANOVA$rho_rel <- as.numeric(as.character(df_ANOVA$rho_rel))
df_ANOVA$rho_ent <- as.numeric(as.character(df_ANOVA$rho_ent))

# Descriptive statistics
with(df_ANOVA, do.call(rbind, tapply(rho_conc, BaselineQ, function(x) c(M = mean(x), SD = sd(x)))))
with(df_ANOVA, do.call(rbind, tapply(n_word, BaselineQ, function(x) c(M = mean(x), SD = sd(x)))))
with(df_ANOVA, do.call(rbind, tapply(LexAmbigSent, BaselineQ, function(x) c(M = mean(x), SD = sd(x)))))
with(df_ANOVA, do.call(rbind, tapply(SynAmbigSent, BaselineQ, function(x) c(M = mean(x), SD = sd(x)))))

#view spread with histograms

#with(df_ANOVA , hist(SynAmbigSent, 
#	main="User Story Syntactic Ambiguity \n\n", 
#	xlab="Syntactic Ambiguity (Sentence)", 
#	border="black", 
#	col="blue",
#	xlim=c(-1000,3600),
#   	breaks=seq(-1000,3600, l=10),
#	axes = TRUE))

#axis(side=1, at=seq(-1000,3600, 2500))

#abline(v = mean(df_ANOVA$SynAmbigSent),
# 	col = "orange",
# 	lwd = 2)

#abline(v = median(df_ANOVA$SynAmbigSent),
# 	col = "red",
# 	lwd = 2)

#par(cex.axis=0.75)

#legend("bottomright", # location of legend within plot area
# 	c("Mean", "Median", "±2SD"),
# 	col = c("Red", "Orange", "Black"), lty = c(6, 1, 2), lwd = c(2, 1, 1),
#      xpd=TRUE, inset=c(0,1), cex=0.7, bty='n')


#Computing mean and standard deviations
#m   <- mean(df_ANOVA$SynAmbigSent)
#std <- sd(df_ANOVA$SynAmbigSent)
#v = m + c(0, 2*std, -2*std)

#Plotting mean and ±2SD values
#abline(v = m + c(0, 2*std, -2*std), lty=c(1,2,2))

#3D scatter plot
#library(scatterplot3d) 
#attach(df_ANOVA) 
#s3d <-scatterplot3d(BaselineQ,LexAmbigSent,SynAmbigSent, pch=16, highlight.3d=TRUE,
#  type="h", main="3D Scatterplot")
#fit <- lm(BaselineQ~LexAmbigSent+SynAmbigSent) 
#s3d$plane3d(fit)

#correlation matrix
#library(gclus)
#dta <- df_ANOVA[c(4,6,9,12,15,16)] # get data 
#dta.r <- abs(cor(dta)) # get correlations
#dta.col <- dmat.color(dta.r) # get colors
# reorder variables so those with highest correlation
# are closest to the diagonal
#dta.o <- order.single(dta.r) 
#cpairs(dta, dta.o, panel.colors=dta.col, gap=.5,
#main="Variables Ordered and Colored by Correlation" )

# a scatter plot of matrices, with bivariate scatter plots below the diagonal, histograms 
#on the diagonal, and the Pearson correlation above the diagonal.

#library(psych)
#pairs.panels(df_ANOVA[c(6,9,12,15,16)], 
 #            method = "pearson", # correlation method
  #           hist.col = "#00AFBB",
   #          density = TRUE,  # show density plots
    #         ellipses = TRUE # show correlation ellipses
     #        )

#### Assumption 1: relationship is linear########
## Linear regression requires: 
#1. Linear relationship
#2. Multivariate normality
#3. No or little multicollinearity
#4. No auto-correlation
#5. Homoscedasticity

# test for linear relationship between independent variable and predictors
data<-df_ANOVA[c(6,9,12,15,16)]

#plot(data)

# testing for normality of predictors with histogram or a Q-Q-Plot or with GOF
# test like the Kolmogorov-Smirnov test. 
#library("car")
#qqPlot(data$n_word)

# test for independence / collinearity of BaselineQ predictors

#fit <- lm(BaselineQ ~ n_word + rho_conc + LexAmbigSent + SynAmbigSent, data=df_ANOVA )
#par(mfrow=c(2,2))
#plot(fit)

# Correlation matrix chart
#library(GGally)
#ggpairs(data)

#Farrar Glauber Test for collinearity
#source: https://datascienceplus.com/multicollinearity-in-r/

#library(mctest)
#omcdiag(data,data$BaselineQ, conf = 0.99)
#imcdiag(data,data$BaselineQ)

#library(ppcor)
#pcor(data, method = "pearson")

#### Assumption 2: relationship is ordinal, interval##########
#data$BaselineQ2 <- round(data$BaselineQ2,2)
data$BaselineQ2 <- as.factor(data$BaselineQ) 
data <- within(data, BaselineQ2 <- relevel(BaselineQ2, ref = 5))
data$BaselineQ2 <- relevel(data$BaselineQ2, ref = "55.5555555555556")


## fit ordered logit model and store results 'm'
m <- polr(BaselineQ2 ~ n_word + rho_conc + LexAmbigSent + SynAmbigSent, data = data, Hess = TRUE) 
## view a summary of the model
summary(m)

# p values / t test for coefficients
#ctable <- coef(summary(m))
## calculate and store p values
#p <- pnorm(abs(ctable[, "t value"]), lower.tail = FALSE) * 2

## combined table
#ctable <- cbind(ctable, "p value" = p)
#ci <- confint(m) # default method gives profiled CIs

exp(coef(m))
## OR and CI
exp(cbind(OR = coef(m), ci))

#GOF Likelihood ratio test
m_trim <- polr(BaselineQ2 ~ n_word + LexAmbigSent, data = data, Hess = TRUE) 

#library(lmtest)
#lrtest(m, m_trim)
				
#psuedo R2
library(pscl)
pR2(m)
pR2(m_trim)

# Calculate Relative Importance for Each Predictor

#To do so, collect all McFadden's R2's according to each 
#possible subset including or omitting each predictor 
#and average them 