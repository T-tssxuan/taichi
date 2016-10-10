# Table Wifi ap

####  table name: WIFI_AP_Passenger_Records_chusai_1stround.csv
三个字段分别为：wifi_ap_tag(字符串)，描述WIFI接入的AP点；passenger_count(整数)，描述在某一时刻接入该WIFI AP的设备数量； time_stamp(字符串)，描述该时刻（精确到秒） 。下面的例子是这张表的实际数据：

| wifi_ap_tag | passenger_count | time_stamp |
| - | - | 
| E1-1A-1<E1-1-01> | 15 | 2016-09-10-18-55-04 |
| E1-1A-2<E1-1-02> | 15 | 2016-09-10-18-55-04 |
| E1-1A-3<E1-1-03> | 38 | 2016-09-10-18-55-04 |

#### Data preprocess
1. Gathering the information based on the tags.
2. Gathering the variation sequence for different time granularity.
3. Gathering the total variation for each section for different size.


#### Infomation gathering
1. At each moment the number of people connected to each AP.
2. The relation to each Ap, such as the **tag name**, **common prefix**.
3. Spacial area of the airport such as the **boarding gate**, **security checkpoint**, **checking**, these place has great difference with others.

#### May be useful information
1. Based their's **variation**, such as: each_minute_variation, each_10_minute_variation or variation_deviation_under_the_given_value.
2. Base on their's **number of users**.
3. Considerate **the tags relation** for the APs.
4. The time approaching the plane taking off, the time between the scheduled and the real time take off.

#### Model for APs
1. Each AP can be regard as a individual entity, and it can interact with the surrounding APs, so reasons conduct it's changing can be concluded as follow actions: **user off line**, **user on line**, **user leaved**, **user enter**.
2. Number of APs can make up a bigger AP, which is in a section we regard many APs as a big AP. We note the bigger AP as **L-X-AP**, `'L': means level, 'X': means the number of level`, the minimal is 0, so the individual AP is a L-0-AP.
3. All other things including, **a plane take off**, **people get ticket**, **people enter the air port**, and other things can be corresponded to the four actions of AP.
