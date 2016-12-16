library(ggplot2)
library(lubridate)
library(stargazer)
library(texreg)
library(lme4)
library(lmerTest)
library(gmodels) # Contains CrossTable
library(MASS)
library(pscl)
library(digest)


set.seed(1477881815)
rm(list=ls())
tweet_days <- read.csv("data/twitter_notices_accounts_tweets_per_day_080116-112116_v30_pruned_42days_user_data_v3_no_json.csv", sep="\t")
tweet_days$user_json <- NULL
tweet_days$after_notice <- tweet_days$day_num > 0

tweet_days$created_at <- as.POSIXct(tweet_days$user_created_at, origin="1970-01-01", tz="UTC")
tweet_days$user.year <- year(tweet_days$created_at)

tweet_days$user_hash <- sapply(tweet_days$screen_name, digest, algo = "sha1")

tweet_days$user.year.rescaled <- tweet_days$user.year - min(tweet_days$user.year)

########################################################
############ UNIVARIATE STATISTICS

## tweets_per_day
summary(tweet_days$tweets_per_day)
hist(tweet_days$tweets_per_day)
hist(log1p(tweet_days$tweets_per_day))

## day_num
summary(tweet_days$day_num)
hist(tweet_days$day_num)

## after_notice
summary(tweet_days$after_notice)

## user_default_profile
summary(tweet_days$user_default_profile)

## user.year
summary(tweet_days$user.year.rescaled)
hist(tweet_days$user.year.rescaled)

## verified
summary(tweet_days$user_verified)

## user_default_profile
summary(tweet_days$user_default_profile)

## user_default_profile_image
summary(tweet_days$user_default_profile_image)

## user_statuses_count
summary(tweet_days$user_statuses_count)
hist(tweet_days$user_statuses_count)
hist(log1p(tweet_days$user_statuses_count))

tweet_days$log_user_statuses_count <- log1p(tweet_days$user_statuses_count)

#unique(tweet_days$user_id)

##########################################
## DEPENDENT VARIABLE BY USER
screen_names <- unique(tweet_days$screen_name)
s_tweet_days <- subset(tweet_days, screen_name %in% sample(screen_names, 10))

ggplot(s_tweet_days, aes(factor(user_id), tweets_per_day, color=after_notice)) +
  geom_violin() +
  coord_flip() +
  ggtitle("Tweets Per Day of a Random Sample of Accounts")

ggplot(s_tweet_days, aes(factor(user_id), log1p(tweets_per_day), color=after_notice)) +
  geom_violin() +
  coord_flip() +
  ggtitle("log1p(Tweets Per Day) of a Random Sample of Accounts")

##########################################
##########################################
## MODELING: LINEAR REGRESSION OF LOG-TRANSFORMED DV
##########################################
tds <- subset(tweet_days, day_num!=0)

summary(lt1<- lmer(log1p(tweets_per_day) ~ 1 + (1|user_hash), data=tds))
summary(lt2<- lmer(log1p(tweets_per_day) ~ log_user_statuses_count + user.year.rescaled + day_num + user_verified + user_default_profile_image + (1|user_hash), data=tds))
summary(lt3<- lmer(log1p(tweets_per_day) ~ log_user_statuses_count + user.year.rescaled + day_num + user_verified + user_default_profile_image + after_notice + (1|user_hash), data=tds))
summary(lt4<- lmer(log1p(tweets_per_day) ~ log_user_statuses_count + user.year.rescaled + day_num + user_verified + user_default_profile_image + after_notice + day_num:after_notice + (1|user_hash), data=tds))

htmlreg(list(lt1, lt2,lt3,lt4))

summary(lt4)

##########################################
##########################################
## MODELING: PREDICTING ZEROES IN TWEETS PER DAY
tweet_days$zero.tweets <- tweet_days$tweets_per_day == 0

summary(z1 <- glmer(zero.tweets ~ 1 + (1|screen_name),data=tweet_days, family=binomial))
summary(z2 <- glmer(zero.tweets ~ log_user_statuses_count + (1|screen_name),data=tweet_days, family=binomial))

##########################################
##########################################
## MODELING: LINEAR REGRESSION OF NEGATIVE BINOMIAL DV
##########################################
summary(nb1<- glmer.nb(tweets_per_day ~ 1 + (1|screen_name), data=tweet_days))
summary(nb2<- glmer.nb(tweets_per_day ~ log_user_statuses_count + user.year.rescaled + day_num + user_verified + user_default_profile_image + (1|screen_name), data=tweet_days))
summary(nb3<- glmer.nb(tweets_per_day ~ log_user_statuses_count + user.year.rescaled + day_num + user_verified + user_default_profile_image + after_notice + (1|screen_name), data=tweet_days))
summary(nb4<- glmer.nb(tweets_per_day ~ log_user_statuses_count + user.year.rescaled + day_num + user_verified + user_default_profile_image + after_notice + day_num:after_notice + (1|screen_name), data=tweet_days))





##########################################
##########################################
## PLOTTING: LOG-TRANSFORMED DV LINEAR MODEL
##########################################
# log1p(tweets_per_day) ~
# log_user_statuses_count + user.year.rescaled + 
#   day_num + user_verified + user_default_profile_image + after_notice + 
#   day_num:after_notice + (1|screen_name)

### GENERATE SIMULATED DATASET
m=lt4
cat1 <-NULL
pf <-NULL
p<-NULL
p = data.frame(day_num = seq(min(tweet_days$day_num), max(tweet_days$day_num), 1))

p$log_user_statuses_count = mean(tweet_days$log_user_statuses_count)
p$user_verified = "False"
p$user_default_profile_image = "False"
p$after_notice <- p$day_num > 0
p$user.year.rescaled <- mean(tweet_days$user.year.rescaled)
p$user_hash = "ce932bf2cce8a30cf1d13dcf059db18656b2861a"
p <- subset(p,day_num!=0)


cat1 <-predict(m, newdata=p, type="link",conf.int=TRUE, se.fit=TRUE)

critval <- 1.96

pf <- p
pf$log_tweets_per_day <- cat1
# pf$log_upr <- cat1$fit + (critval * cat1$se.fit)
# pf$log_lwr <- cat1$fit - (critval * cat1$se.fit)
# pf$log_tweets_per_day <- cat1$fit

#pf$tweets_per_day <- m$family$linkinv(pf$log_article_count)
#pf$upr2 <- m$family$linkinv(pf$log_upr)
#pf$lwr2 <- m$family$linkinv(pf$log_upr)

### PLOT FULL VERSION
ggplot(pf, aes(x = day_num, y=log_tweets_per_day, colour=after_notice)) +
#  geom_point(data=tweet_days,aes(x=day_num, y=log1p(tweets_per_day)), alpha=.9) +
  ylim(0,1.5) +
  geom_line(data=pf,size = 1)

### PLOT FULL VERSION
ggplot(pf, aes(x = day_num, y=exp(log_tweets_per_day), colour=after_notice)) +
  #  geom_point(data=tweet_days,aes(x=day_num, y=log1p(tweets_per_day)), alpha=.9) +
  ylim(0,3.5) +
  theme(text = element_text(size=15), axis.text = element_text(size=15)) + 
  geom_line(data=pf,size = 2) +
  geom_vline(xintercept=0, linetype="dotted") +
  scale_colour_discrete(name="Tweet Period",labels=c("Before Takedown", "After Takedown")) +
  xlab("Day Number, From 42 Days Before to 42 Days After Receiving a Notice") +
  ylab("Predicted Tweets Per Day for a Prototypical User") +
  ggtitle("After Receiving a Takedown Notice, Users Sent Fewer Tweets Per Day And Tweeted Less Over Time, on Average")
