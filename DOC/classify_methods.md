# Map Classify Methods Descriptions

## EqualInterval

  **Description:** This method divides the range of data values into a user-specified number of equal-sized sub-ranges or intervals. Each interval has the same width, and the class breaks are automatically calculated based on the data's range.
  
  **Usecases:** Ideal for visualizing data that has a fairly uniform or familiar distribution. It's a simple, easy-to-understand method, but can produce misleading maps if the data is heavily skewed.
  
## FisherJenks

**Description:** An optimal classification method that minimizes the sum of squared differences within each class. It finds the most "natural" groupings by maximizing homogeneity within classes and heterogeneity between them.

**Usecases:** Recommended for choropleth maps where the goal is to reveal natural clusters in the data. It's especially useful for data with a non-uniform distribution.

## FisherJenksSampled

**Description:** A faster, approximate version of the FisherJenks algorithm, designed for very large datasets. It performs the classification on a random sample of the data to improve performance.
**Usecases:** For large datasets where a full FisherJenks classification is too computationally intensive. This method offers a good trade-off between speed and accuracy.

## HeadTailBreaks

**Description:** A classification method specifically designed for heavy-tailed distributions, where many observations are small and a few are very large. It recursively divides the data at the mean, separating the "head" (values above the mean) and "tail" (values below the mean).

**Usecases:** Ideal for heavy-tailed data such as city populations, river networks, or income distributions. It's a simple and effective way to handle highly skewed data.

## JenksCaspall

**Description:** A greedy iterative algorithm for map classification. It begins with an initial set of classes and then moves observations between classes to improve the fit, based on maximizing the homogeneity within classes.

**Usecases:** An alternative to FisherJenks, especially useful when an iterative, local-optimization approach is suitable.

## JenksCaspallForced

**Description:** A variation of the JenksCaspall algorithm that forces some non-optimal moves to help escape local optima and potentially find a better solution.

**Usecases:** Use when the standard JenksCaspall algorithm might get stuck in a suboptimal solution. It can be more computationally intensive but may produce a better classification.

## JenksCaspallSampled

**Description:** A sampled version of the JenksCaspall algorithm for faster execution on large datasets. It's a more efficient alternative to the full JenksCaspall algorithm for large-scale data.

**Usecases:** For large datasets, this offers a balance between computational speed and quality of classification.

## MaxP

**Description:** A regionalization method that creates contiguous spatial regions or bins. It maximizes a specified spatial statistic (p-statistic) to group observations into spatially coherent classes.

**Usecases:** For applications where both attribute similarity and spatial contiguity are important, such as in spatial analysis or redistricting.

## MaximumBreaks

**Description:** This method identifies class boundaries by finding the largest differences between adjacent values in the sorted data. It prioritizes large "jumps" in the data to define the class intervals.

**Usecases:** Good for datasets with a few large jumps in values, but can be sensitive to outliers.

## NaturalBreaks

**Description:** An optimization algorithm that partitions data into classes based on natural groupings inherent in the data. It attempts to minimize the variance within classes. In mapclassify, it is based on a k-means clustering approach.

**Usecases:** A popular, general-purpose method for choropleth maps, especially when the data has a clustered distribution. It can produce visually pleasing and intuitive maps.

## Quantiles

**Description:** This method divides the data so that each class has approximately the same number of observations. The class breaks are at the cumulative quantiles of the data.

**Usecases:** Useful when you want to emphasize the relative position of observations in the distribution. It's effective for non-uniformly distributed data, but can place similar-valued observations into different classes.

## Percentiles

**Description:** Similar to quantiles but allows the user to specify custom percentiles to define the class breaks. This provides fine-grained control over the classification.

**Usecases:** When you have a specific, custom set of percentile thresholds in mind. Can be used for custom analyses and visualizations.

## PrettyBreaks

**Description:** A classification scheme that automatically generates rounded, "pretty" class breaks. The class breaks are chosen to be aesthetically pleasing and easy to read, such as multiples of 1, 2, or 5.

**Usecases:** For creating maps intended for a general audience, where readability and visual appeal are prioritized over statistical precision. Note that this can lead to uneven class sizes.

## UserDefined

**Description:** This method allows the user to manually define the class break values. It provides complete control over the classification process.

**Usecases:** When specific thresholds are required for a particular analysis or policy context, or when comparing against a known standard.