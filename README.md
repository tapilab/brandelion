# brandelion

**Social media brand analysis**

1. Set an environmental variable for the `brandelion` data directory:

  `export BRANDELION=/data/brandelion`

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

5. Create a file called `exemplars.txt` containing exemplars for the dimension you wish to analyze. For example, here we choose environmental friendliness.
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
