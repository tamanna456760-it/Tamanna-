import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('warking')


class BDKingAI:
    def __init__(self, data=tamanna456760-it):
        self.system_name = "BD-KING-R7"
        self.version = "R7.2.1"

        if data is not None:
            self.data = data.copy()
            self.clean_data()
        else:
            self.data = None

        # Initialize AI components
        self.scaler = StandardScaler()
        self.pca = PCA()
        self.cluster_model = KMeans(n_clusters=3, random_state=42)

        plt.style.use('dark_background')
        sns.set_palette("husl")

    def clean_data(self):
        """Advanced data cleaning for BD-KING-R7"""
        if self.data is None:
            return

        # Handle missing values
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns
        categorical_cols = self.data.select_dtypes(include=['object']).columns

        for col in numerical_cols:
            if self.data[col].isnull().sum() > 0:
                self.data[col].fillna(self.data[col].median(), inplace=True)

        for col in categorical_cols:
            if self.data[col].isnull().sum() > 0:
                self.data[col].fillna(self.data[col].mode()[
                                      0] if not self.data[col].mode().empty else 'Unknown', inplace=True)

    def comprehensive_analysis(self):
        """Perform comprehensive AI-powered analysis"""
        if self.data is None:
            return {"error": "No data available"}

        analysis = {
            "system": self.system_name,
            "analysis_timestamp": pd.Timestamp.now().isoformat(),
            "data_profile": self._get_data_profile(),
            "statistical_analysis": self._statistical_analysis(),
            "pattern_detection": self._detect_patterns(),
            "anomaly_detection": self._detect_anomalies(),
            "correlation_network": self._correlation_analysis(),
            "clustering_analysis": self._perform_clustering(),
            "trend_analysis": self._analyze_trends()
        }

        return analysis

    def _get_data_profile(self):
        """Generate comprehensive data profile"""
        profile = {
            "dimensions": self.data.shape,
            "memory_usage": f"{self.data.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
            "data_types": self.data.dtypes.astype(str).to_dict(),
            "completeness_score": self._calculate_completeness_score(),
            "quality_metrics": self._calculate_quality_metrics()
        }
        return profile

    def _calculate_completeness_score(self):
        """Calculate data completeness score"""
        total_cells = self.data.size
        missing_cells = self.data.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        return round(completeness, 2)

    def _calculate_quality_metrics(self):
        """Calculate data quality metrics"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        metrics = {
            "numerical_columns": len(numerical_cols),
            "categorical_columns": len(self.data.select_dtypes(include=['object']).columns),
            "duplicate_rows": self.data.duplicated().sum(),
            "zero_values": (self.data[numerical_cols] == 0).sum().sum(),
            "outlier_percentage": self._calculate_outlier_percentage()
        }
        return metrics

    def _calculate_outlier_percentage(self):
        """Calculate percentage of outliers in numerical data"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns
        outlier_count = 0
        total_count = 0

        for col in numerical_cols:
            Q1 = self.data[col].quantile(0.25)
            Q3 = self.data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = self.data[(self.data[col] < lower)
                                  | (self.data[col] > upper)]
            outlier_count += len(outliers)
            total_count += len(self.data)

        return round((outlier_count / total_count) * 100, 2) if total_count > 0 else 0

    def _statistical_analysis(self):
        """Perform advanced statistical analysis"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        stats_summary = {}
        for col in numerical_cols:
            data = self.data[col].dropna()
            stats_summary[col] = {
                "mean": round(data.mean(), 4),
                "std": round(data.std(), 4),
                "variance": round(data.var(), 4),
                "skewness": round(stats.skew(data), 4),
                "kurtosis": round(stats.kurtosis(data), 4),
                "normality_test": round(stats.shapiro(data)[1], 4),
                "confidence_interval": [
                    round(data.mean() - 1.96 * data.std() /
                          np.sqrt(len(data)), 4),
                    round(data.mean() + 1.96 *
                          data.std() / np.sqrt(len(data)), 4)
                ]
            }

        return stats_summary

    def _detect_patterns(self):
        """Detect patterns in the data"""
        patterns = {
            "seasonality": self._detect_seasonality(),
            "trends": self._detect_trends(),
            "correlation_clusters": self._find_correlation_clusters(),
            "data_distribution": self._analyze_distributions()
        }
        return patterns

    def _detect_seasonality(self):
        """Detect seasonal patterns"""
        # Simplified seasonality detection
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        seasonality = {}
        for col in numerical_cols[:3]:  # Analyze first 3 columns
            data = self.data[col].dropna()
            if len(data) > 10:
                # Simple autocorrelation for seasonality
                autocorr = [data.autocorr(lag=i)
                                          for i in range(1, min(10, len(data)//4))]
                max_autocorr = max(np.abs(autocorr)) if autocorr else 0
                seasonality[col] = {
                    "has_seasonality": max_autocorr > 0.5,
                    "strength": round(max_autocorr, 4)
                }

        return seasonality

    def _detect_trends(self):
        """Detect trends in numerical data"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        trends = {}
        for col in numerical_cols:
            data = self.data[col].dropna()
            if len(data) > 2:
                x = np.arange(len(data))
                slope, _, r_value, _, _ = stats.linregress(x, data)
                trends[col] = {
                    "trend": "increasing" if slope > 0 else "decreasing",
                    "slope": round(slope, 4),
                    "r_squared": round(r_value**2, 4),
                    "strength": "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.5 else "weak"
                }

        return trends

    def _find_correlation_clusters(self):
        """Find clusters of highly correlated variables"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        if len(numerical_cols) < 2:
            return {}

        corr_matrix = self.data[numerical_cols].corr()

        # Find strongly correlated pairs
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_correlations.append({
                        "variables": [corr_matrix.columns[i], corr_matrix.columns[j]],
                        "correlation": round(corr_val, 4),
                        "type": "positive" if corr_val > 0 else "negative"
                    })

        return {"strong_correlations": strong_correlations[:10]}

    def _analyze_distributions(self):
        """Analyze data distributions"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        distributions = {}
        for col in numerical_cols:
            data = self.data[col].dropna()
            distributions[col] = {
                "distribution_type": self._classify_distribution(data),
                "uniqueness": round(data.nunique() / len(data), 4),
                "entropy": round(stats.entropy(data.value_counts(normalize=True)), 4)
            }

        return distributions

    def _classify_distribution(self, data):
        """Classify the type of distribution"""
        if len(data) < 10:
            return "insufficient_data"

        # Test for normal distribution
        _, p_normal = stats.normaltest(data)

        if p_normal > 0.05:
            return "normal"
        elif stats.skew(data) > 1:
            return "right_skewed"
        elif stats.skew(data) < -1:
            return "left_skewed"
        else:
            return "unknown"

    def _detect_anomalies(self):
        """Detect anomalies using multiple methods"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        anomalies = {}
        for col in numerical_cols:
            data = self.data[col].dropna()

            # IQR method
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            iqr_anomalies = data[(data < lower) | (data > upper)]

            # Z-score method
            z_scores = np.abs(stats.zscore(data))
            z_anomalies = data[z_scores > 3]

            anomalies[col] = {
                "iqr_anomalies": len(iqr_anomalies),
                "z_score_anomalies": len(z_anomalies),
                "anomaly_percentage": round(len(iqr_anomalies) / len(data) * 100, 2)
            }

        return anomalies

    def _correlation_analysis(self):
        """Advanced correlation analysis"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        if len(numerical_cols) < 2:
            return {}

        corr_matrix = self.data[numerical_cols].corr()

        # Find correlation patterns
        high_corr = []
        moderate_corr = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                pair = {
                    "variables": [corr_matrix.columns[i], corr_matrix.columns[j]],
                    "correlation": round(corr_val, 4)
                }

                if abs(corr_val) > 0.8:
                    high_corr.append(pair)
                elif abs(corr_val) > 0.5:
                    moderate_corr.append(pair)

        return {
            "high_correlations": high_corr[:5],
            "moderate_correlations": moderate_corr[:5],
            "correlation_matrix_summary": {
                "mean_abs_correlation": round(corr_matrix.abs().mean().mean(), 4),
                "max_correlation": round(corr_matrix.abs().max().max(), 4)
            }
        }

    def _perform_clustering(self):
        """Perform clustering analysis"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        if len(numerical_cols) < 2:
            return {}

        # Use first 5 numerical columns for clustering
        cluster_data = self.data[numerical_cols[:5]].dropna()

        if len(cluster_data) < 10:
            return {}

        # Standardize data
        scaled_data = self.scaler.fit_transform(cluster_data)

        # Perform clustering
        clusters = self.cluster_model.fit_predict(scaled_data)

        return {
            "n_clusters": len(np.unique(clusters)),
            "cluster_sizes": np.bincount(clusters).tolist(),
            "silhouette_score": round(self._calculate_silhouette_score(scaled_data, clusters), 4)
        }

    def _calculate_silhouette_score(self, data, clusters):
        """Calculate silhouette score for clustering"""
        from sklearn.metrics import silhouette_score
        return silhouette_score(data, clusters)

    def _analyze_trends(self):
        """Analyze trends in the data"""
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns

        trends = {}
        for col in numerical_cols:
            data = self.data[col].dropna()
            if len(data) > 10:
                # Simple trend analysis
                x = np.arange(len(data))
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    x, data)

                trends[col] = {
                    "trend_direction": "upward" if slope > 0 else "downward",
                    "trend_strength": round(abs(r_value), 4),
                    "significance": "significant" if p_value < 0.05 else "not_significant",
                    "rate_of_change": round(slope, 4)
                }

        return trends

    def generate_ai_insights(self):
        """Generate AI-powered insights"""
        if self.data is None:
            return ["No data available for analysis"]

        insights = []

        # Data quality insights
        completeness = self._calculate_completeness_score()
        if completeness < 90:
            insights.append(
                f"⚠️ Data completeness is {completeness}%. Consider data cleaning.")

        # Pattern insights
        patterns = self._detect_patterns()
        if patterns.get('seasonality'):
            for col, seasonality_info in patterns['seasonality'].items():
                if seasonality_info.get('has_seasonality'):
                    insights.append(
                        f"📈 Seasonal pattern detected in {col} (strength: {seasonality_info['strength']})")

        # Correlation insights
        correlations = self._correlation_analysis()
        if correlations.get('high_correlations'):
            high_corr = correlations['high_correlations'][0]
            insights.append(f"🔗 Strong correlation between {high_corr['
