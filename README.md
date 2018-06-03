# brandelion

**Social media brand analysis**

1. Copy the .brandelion config file to your home directory `~/.brandelion`.  Edit the config file to specify the output path and the [Google Search API keys](https://developers.google.com/custom-search/json-api/v1/overview) (the latter are only needed if you'll be fetching exemplars by keyword).

 
2. Create a list of brand Twitter accounts and store in `$BRANDELION/brands.txt`.
  ```
  $ cat $BRANDELION/brands.txt
    7UP
    100percentpure
    18Rabbits
    34Degrees
    5hourenergy
   ```

3. Collect followers for each brand (here, we limit to 100 followers per brand, for demonstration purposes).
   ```
   $ brandelion collect --followers -i $BRANDELION/brands.txt  -o $BRANDELION/brand_followers.txt -m 100
   Fetching followers for accounts in /data/brandelion/brands.txt
   collecting followers for 7UP
   fetched 5000 more followers for 259370909
   collecting followers for 100percentpure
   fetched 5000 more followers for 26286294
   collecting followers for 18Rabbits
   fetched 1183 more followers for 29249985
   collecting followers for 34Degrees
   fetched 1934 more followers for 80340314
   collecting followers for 5hourenergy
   fetched 5000 more followers for 33666177
   ```

4. Collect tweets for each brand (here, we limit to 200 tweets per brand, for demonstration purposes).
   ```
   $ brandelion collect --tweets -i $BRANDELION/brands.txt  -o $BRANDELION/brand_tweets.json -m 200
   fetching tweets for accounts in /data/brandelion/brands.txt

   Fetching tweets for 7UP
   fetched 199 more tweets for 7UP
   fetched 200 more tweets for 7UP

   Fetching tweets for 100percentpure
   fetched 200 more tweets for 100percentpure

   Fetching tweets for 18Rabbits
   fetched 198 more tweets for 18Rabbits
   fetched 200 more tweets for 18Rabbits

   Fetching tweets for 34Degrees
   fetched 200 more tweets for 34Degrees

   Fetching tweets for 5hourenergy
   fetched 200 more tweets for 5hourenergy
   ```

5. Create a list of exemplar Twitter accounts. You can either do this manually, or use the collect script to search by keyword. E.g., 
   ```
   $ brandelion collect --exemplars --query environment --output exemplars.txt
    ```
    will search for accounts on Twitter Lists that match the keyword "environment". The output file stores how many distinct list this account appears on, which you can use to filter to the most common accounts.

   Store the final list of exemplars in $BRANDELION/exemplars.txt
   ```
   $ cat $BRANDELION/exemplars.txt
   GreenPeace
   EnvDefenseFund
   globalgreen
   OurOcean
   ClimateReality
   ```

6. Repeat the follower and tweet collection steps above, writing to `exemplar_followers.txt` and `exemplar_tweets.json`:
   ```
   $ brandelion collect --followers -i $BRANDELION/exemplars.txt  -o $BRANDELION/exemplar_followers.txt -m 100
   Fetching followers for accounts in /data/brandelion/exemplars.txt
   collecting followers for GreenPeace
   fetched 5000 more followers for 3459051
   collecting followers for EnvDefenseFund
   fetched 5000 more followers for 20068053
   collecting followers for globalgreen
   fetched 5000 more followers for 19409588
   collecting followers for OurOcean
   fetched 5000 more followers for 71019945
   collecting followers for ClimateReality
   fetched 5000 more followers for 16958346

   $ brandelion collect --tweets -i $BRANDELION/exemplars.txt  -o $BRANDELION/exemplar_tweets.json -m 200
   fetching tweets for accounts in /data/brandelion/exemplars.txt

   Fetching tweets for GreenPeace
   fetched 200 more tweets for GreenPeace

   Fetching tweets for EnvDefenseFund
   fetched 200 more tweets for EnvDefenseFund

   Fetching tweets for globalgreen
   fetched 200 more tweets for globalgreen

   Fetching tweets for OurOcean
   fetched 200 more tweets for OurOcean

   Fetching tweets for ClimateReality
   fetched 200 more tweets for ClimateReality
   ```

7. Collect tweets for a representative sample of accounts, stored in `sample.txt`.
   ```
   $ cat $BRANDELION/sample.txt
   RedCross
   TobaccoFreeKids
   CFR_org
   Habitat_org
   PRI

   $ brandelion collect --tweets -i $BRANDELION/sample.txt  -o $BRANDELION/sample_tweets.json -m 200
   fetching tweets for accounts in /data/brandelion/sample.txt

   Fetching tweets for RedCross
   fetched 200 more tweets for RedCross

   Fetching tweets for TobaccoFreeKids
   fetched 200 more tweets for TobaccoFreeKids

    Fetching tweets for CFR_org
   fetched 200 more tweets for CFR_org

   Fetching tweets for Habitat_org
   fetched 200 more tweets for Habitat_org

   Fetching tweets for PRI
   fetched 200 more tweets for PRI
   ```
7. Compute the social scores between the brands and the exemplars, based on network properties. (In this example, there is no follower overlap, so scores are 0.)
   ```
   $ brandelion analyze --network --brand-followers $BRANDELION/brand_followers.txt --exemplar-followers $BRANDELION/exemplar_followers.txt --output $BRANDELION/social_scores.txt
   read follower data for 5 brands and 5 exemplars
   results written to /data/brandelion/social_scores.txt

   $ cat /data/brandelion/social_scores.txt
   5hourenergy 0.000000
   18Rabbits 0.000000
   7UP 0.000000
   100percentpure 0.000000
   34Degrees 0.000000
   ```

8. Compute scores for each brand based on textual overlap with exemplars.
   ```
   $ brandelion analyze --text --brand-tweets $BRANDELION/brand_tweets.json --exemplar-tweets $BRANDELION/exemplar_tweets.json --sample-tweets $BRANDELION/sample_tweets.json --output $BRANDELION/text_scores.txt
   read 5 exemplars, 5 brands, 5 sample accounts
   top 10 ngrams:
   york city=5
   000 people=4
   the planet=4
   hashtagpeoplesclimate march=4
   hashtagpeoplesclimate hashtagpeoplesclimate=4
   marching for=4
   hashtagactonclimate hashtagactonclimate=4
   join the=4
   climate action=4
   our climate=4

   $ cat $BRANDELION/text_scores.txt
   7UP 0.053655
   100percentpure 0.100966
   18Rabbits 0.105482
   34Degrees 0.086343
   5hourenergy 0.090429
   ```
