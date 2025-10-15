
"""Keyword configuration for project matching"""

BLOCKCHAIN_KEYWORDS = [
    'blockchain',
    'distributed ledger',
    'dlt',
    'smart contract',
    'decentralized',
    'web3',
    'tokenization',
    'cryptocurrency',
    'consensus',
    'immutable',
    'hyperledger',
    'ethereum'
]

PRIVACY_KEYWORDS = [
    'privacy',
    'zero knowledge',
    'zk',
    'zk-snark',
    'zk-stark',
    'confidential',
    'secure',
    'encryption',
    'tee',
    'trusted execution',
    'privacy-preserving',
    'differential privacy',
    'homomorphic',
    'mpc',
    'secure multi-party',
    'anonymization',
    'sgx',
    'trustzone'
]

DATA_GOVERNANCE_KEYWORDS = [
    'data sharing',
    'data space',
    'data governance',
    'interoperability',
    'trust',
    'traceability',
    'provenance',
    'audit',
    'compliance',
    'data sovereignty',
    'gdpr',
    'data protection',
    'access control'
]

AI_KEYWORDS = [
    'artificial intelligence',
    'machine learning',
    'deep learning',
    'neural network',
    'federated learning',
    'ai model',
    'training data'
]

IOT_KEYWORDS = [
    'iot',
    'internet of things',
    'sensors',
    'edge computing',
    'smart devices',
    'connected devices'
]

WEIGHTS = {
    'blockchain': 3,
    'privacy': 3,
    'data_governance': 2,
    'ai': 2,
    'iot': 2
}

MIN_SCORE_THRESHOLD = 3
HIGH_PRIORITY_THRESHOLD = 9
MEDIUM_PRIORITY_THRESHOLD = 6