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


tweet_days <- read.csv("data/twitter_notices_accounts_tweets_per_day_080116-112116_v30_pruned_42days_user_data.csv", sep="\t")
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

##########################################
## DEPENDENT VARIABLE BY USER
screen_names <- unique(tweet_days$screen_name)
s_tweet_days <- subset(tweet_days, screen_name %in% sample(screen_names, 20))

ggplot(s_tweet_days, aes(user_hash, tweets_per_day, color=after_notice)) +
  geom_violin() +
  coord_flip() +
  ggtitle("Tweets Per Day of a Random Sample of Accounts")

ggplot(s_tweet_days, aes(user_hash, log1p(tweets_per_day), color=after_notice)) +
  geom_violin() +
  coord_flip() +
  ggtitle("log1p(Tweets Per Day) of a Random Sample of Accounts")


##########################################
##########################################
## MODELING: LINEAR REGRESSION OF LOG-TRANSFORMED DV
##########################################

summary(lt1<- lmer(log1p(tweets_per_day) ~ 1 + (1|screen_name), data=tweet_days))
summary(lt2<- lmer(log1p(tweets_per_day) ~ user.year.rescaled + day_num + user_verified + user_default_profile_image + (1|screen_name), data=tweet_days))
summary(lt3<- lmer(log1p(tweets_per_day) ~ user.year.rescaled + day_num + user_verified + user_default_profile_image + after_notice + (1|screen_name), data=tweet_days))
summary(lt4<- lmer(log1p(tweets_per_day) ~ user.year.rescaled + day_num + user_verified + user_default_profile_image + after_notice + day_num:after_notice + (1|screen_name), data=tweet_days))

htmlreg(list(lt1, lt2,lt3,lt4))

##########################################
##########################################
## MODELING: LINEAR REGRESSION OF NEGATIVE BINOMIAL DV
##########################################
summary(nb1<- glmer.nb(tweets_per_day ~ 1 + (1|screen_name), data=tweet_days))
summary(nb2<- glmer.nb(tweets_per_day ~ user.year.rescaled + day_num + user_verified + user_default_profile_image + (1|screen_name), data=tweet_days))
summary(nb3<- glmer.nb(tweets_per_day ~ user.year.rescaled + day_num + user_verified + user_default_profile_image + after_notice + (1|screen_name), data=tweet_days))
summary(nb4<- glmer.nb(tweets_per_day ~ user.year.rescaled + day_num + user_verified + user_default_profile_image + after_notice + day_num:after_notice + (1|screen_name), data=tweet_days))


