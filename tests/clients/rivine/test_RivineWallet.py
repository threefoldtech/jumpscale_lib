"""
Test module for RivineWallet js9 client
"""


from mnemonic import Mnemonic
from JumpScale9Lib.clients.rivine.RivineWallet import RivineWallet

# create a random seed
m = Mnemonic('english')
seed = m.generate()

# use specific seed
seed = 'festival mobile negative nest valid cheese pulp alpha relax language friend vast'

expected_unlockhashes = [
    '2d85a10ad31f2d505768be5efb417de565a53364d7f0c69a888ca764f4bdbcbb',
    '59e5933416affb97748d5e94fa64f97305075c4ebf971c09a64977839b7087b3',
    '65e5838cfee444cbf98661e2648918ad7b0d622e9b600f1b8271161874cd1d6c',
    '7c75ddbfe744022c2b9be8f38b7049e4878b3e5030910447b0083af2ac5e20db',
    'bc961fa13fd17ea13268d24bf502506325729c07da867d8dc64363a2af9955f6',
]

# create a wallet based on the generated Seed
rivine_wallet = RivineWallet(seed=seed, bc_network='http://185.69.166.13:2015', nr_keys_per_seed=5)
actual_unlockhashes = [key for key in rivine_wallet.keys.keys()] 

assert set(expected_unlockhashes) ==  set(actual_unlockhashes), "Unlockhashes do not match" 

assert type(rivine_wallet.get_current_chain_height()) == int

expected_address_info =\
"""{
    "hashtype": "unlockhash",
    "block": {
        "minerpayoutids": null,
        "transactions": null,
        "rawblock": {
            "parentid": "0000000000000000000000000000000000000000000000000000000000000000",
            "timestamp": 0,
            "pobsindexes": {
                "BlockHeight": 0,
                "TransactionIndex": 0,
                "OutputIndex": 0
            },
            "minerpayouts": null,
            "transactions": null
        },
        "blockid": "0000000000000000000000000000000000000000000000000000000000000000",
        "difficulty": "0",
        "estimatedactivebs": "0",
        "height": 0,
        "maturitytimestamp": 0,
        "target": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ],
        "totalcoins": "0",
        "minerpayoutcount": 0,
        "transactioncount": 0,
        "coininputcount": 0,
        "coinoutputcount": 0,
        "blockstakeinputcount": 0,
        "blockstakeoutputcount": 0,
        "minerfeecount": 0,
        "arbitrarydatacount": 0,
        "transactionsignaturecount": 0
    },
    "blocks": [
        {
            "minerpayoutids": [
                "9e9e509f9d412719ceb0f17ab0a4c950c9a4b2981cd4f9949a2212ec4caa8929"
            ],
            "transactions": [
                {
                    "id": "c2e6f47ff4a089c7fb94ce55fd31b2a2df1964b70eb9fc541b7316643c07abff",
                    "height": 5,
                    "parent": "0dcd365344a9ee912509e965bc0231836324f44cf6eb43695ea7b5bccf817e35",
                    "rawtransaction": {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "ee3a4e9b504d79843dd6b95a7ad3935c1d9ed1eb4c77d4f1e41681d68754174c",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "ee3a4e9b504d79843dd6b95a7ad3935c1d9ed1eb4c77d4f1e41681d68754174c",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "j3a8mMGoGDOwP/egPZC9JG/307DvUc59nIQxe1AZ1GKGxwE9g55vB0Tr56qDjY+GRnCiokOae2HHXp2HDOdkAw=="
                            }
                        ]
                    },
                    "coininputoutputs": null,
                    "coinoutputids": null,
                    "blockstakeinputoutputs": [
                        {
                            "value": "1000000",
                            "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                        }
                    ],
                    "blockstakeoutputids": [
                        "08ae8d80c10f173df0f69b20c5b4a686a1c8ecb1519acaca2ef00c17121cdd36"
                    ]
                }
            ],
            "rawblock": {
                "parentid": "1ef8e34bd17ff733d697eaa88f699d101c2e069b114c51454e7e1ce385d90e7b",
                "timestamp": 1519821294,
                "pobsindexes": {
                    "BlockHeight": 4,
                    "TransactionIndex": 0,
                    "OutputIndex": 0
                },
                "minerpayouts": [
                    {
                        "value": "10000000000000000000000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "transactions": [
                    {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "ee3a4e9b504d79843dd6b95a7ad3935c1d9ed1eb4c77d4f1e41681d68754174c",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "ee3a4e9b504d79843dd6b95a7ad3935c1d9ed1eb4c77d4f1e41681d68754174c",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "j3a8mMGoGDOwP/egPZC9JG/307DvUc59nIQxe1AZ1GKGxwE9g55vB0Tr56qDjY+GRnCiokOae2HHXp2HDOdkAw=="
                            }
                        ]
                    }
                ]
            },
            "blockid": "0dcd365344a9ee912509e965bc0231836324f44cf6eb43695ea7b5bccf817e35",
            "difficulty": "600000000",
            "estimatedactivebs": "0",
            "height": 5,
            "maturitytimestamp": 0,
            "target": [
                0,
                0,
                0,
                7,
                40,
                132,
                246,
                16,
                46,
                189,
                245,
                53,
                61,
                107,
                55,
                34,
                71,
                197,
                45,
                55,
                227,
                55,
                228,
                229,
                100,
                15,
                15,
                218,
                4,
                95,
                124,
                217
            ],
            "totalcoins": "0",
            "minerpayoutcount": 5,
            "transactioncount": 7,
            "coininputcount": 1,
            "coinoutputcount": 3,
            "blockstakeinputcount": 5,
            "blockstakeoutputcount": 6,
            "minerfeecount": 1,
            "arbitrarydatacount": 0,
            "transactionsignaturecount": 6
        },
        {
            "minerpayoutids": [
                "099aa602c0073ea278b086712eac30f47c66b624b2f4719e08280cd7a7307857"
            ],
            "transactions": [
                {
                    "id": "92af92ead2df3a04e0a76b8e0db74592f383f4b4774453870fd6b76ded3a1e2f",
                    "height": 3,
                    "parent": "14c9eea4b952cdcc4ebb7a5f20a43a04353a451591c2c6abf9541469cfca72cf",
                    "rawtransaction": {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "1cf724879114b3e8c56d6ba50f6e25fc3d81bc074d455ffe4c211aaeb157de64",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "1cf724879114b3e8c56d6ba50f6e25fc3d81bc074d455ffe4c211aaeb157de64",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "xkFxpQowb30HsPzEfhapHVBfB1Mimj1QvhzzyMYPF8uydvaFOPZprGLseliFSeW3SPOggf6+rsGv7gE1iixrAQ=="
                            }
                        ]
                    },
                    "coininputoutputs": null,
                    "coinoutputids": null,
                    "blockstakeinputoutputs": [
                        {
                            "value": "1000000",
                            "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                        }
                    ],
                    "blockstakeoutputids": [
                        "7647d2ec842866fd71ade5f12be947f358744d048f2570d5ca232043c5dbe248"
                    ]
                }
            ],
            "rawblock": {
                "parentid": "3a1978f53183d8eeb5dbe52a70131f194978aaf6447eeccacdb840b3f09487ec",
                "timestamp": 1519818383,
                "pobsindexes": {
                    "BlockHeight": 2,
                    "TransactionIndex": 0,
                    "OutputIndex": 0
                },
                "minerpayouts": [
                    {
                        "value": "10000000000000000000000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "transactions": [
                    {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "1cf724879114b3e8c56d6ba50f6e25fc3d81bc074d455ffe4c211aaeb157de64",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "1cf724879114b3e8c56d6ba50f6e25fc3d81bc074d455ffe4c211aaeb157de64",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "xkFxpQowb30HsPzEfhapHVBfB1Mimj1QvhzzyMYPF8uydvaFOPZprGLseliFSeW3SPOggf6+rsGv7gE1iixrAQ=="
                            }
                        ]
                    }
                ]
            },
            "blockid": "14c9eea4b952cdcc4ebb7a5f20a43a04353a451591c2c6abf9541469cfca72cf",
            "difficulty": "600000000",
            "estimatedactivebs": "0",
            "height": 3,
            "maturitytimestamp": 0,
            "target": [
                0,
                0,
                0,
                7,
                40,
                132,
                246,
                16,
                46,
                189,
                245,
                53,
                61,
                107,
                55,
                34,
                71,
                197,
                45,
                55,
                227,
                55,
                228,
                229,
                100,
                15,
                15,
                218,
                4,
                95,
                124,
                217
            ],
            "totalcoins": "0",
            "minerpayoutcount": 3,
            "transactioncount": 5,
            "coininputcount": 1,
            "coinoutputcount": 3,
            "blockstakeinputcount": 3,
            "blockstakeoutputcount": 4,
            "minerfeecount": 1,
            "arbitrarydatacount": 0,
            "transactionsignaturecount": 4
        },
        {
            "minerpayoutids": [
                "41cda66fcc584d3b266c2c1e54756dd15a2c3c0a29bc8bf5c636177cfd615860"
            ],
            "transactions": [
                {
                    "id": "5dd9e90750dc9ded436f1ac298ca3920c7ba89f60a74daf5a5dbdee73bab32be",
                    "height": 4,
                    "parent": "1ef8e34bd17ff733d697eaa88f699d101c2e069b114c51454e7e1ce385d90e7b",
                    "rawtransaction": {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "7647d2ec842866fd71ade5f12be947f358744d048f2570d5ca232043c5dbe248",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "7647d2ec842866fd71ade5f12be947f358744d048f2570d5ca232043c5dbe248",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "lsfJ54PP23kf7WDJiEzziC0q83qnzt34JvlKW5OVRgVqm50xbQcOROrcoWO5ha0BKMi96WYUoopL47o0eBK7BA=="
                            }
                        ]
                    },
                    "coininputoutputs": null,
                    "coinoutputids": null,
                    "blockstakeinputoutputs": [
                        {
                            "value": "1000000",
                            "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                        }
                    ],
                    "blockstakeoutputids": [
                        "ee3a4e9b504d79843dd6b95a7ad3935c1d9ed1eb4c77d4f1e41681d68754174c"
                    ]
                }
            ],
            "rawblock": {
                "parentid": "14c9eea4b952cdcc4ebb7a5f20a43a04353a451591c2c6abf9541469cfca72cf",
                "timestamp": 1519820186,
                "pobsindexes": {
                    "BlockHeight": 3,
                    "TransactionIndex": 0,
                    "OutputIndex": 0
                },
                "minerpayouts": [
                    {
                        "value": "10000000000000000000000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "transactions": [
                    {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "7647d2ec842866fd71ade5f12be947f358744d048f2570d5ca232043c5dbe248",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "7647d2ec842866fd71ade5f12be947f358744d048f2570d5ca232043c5dbe248",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "lsfJ54PP23kf7WDJiEzziC0q83qnzt34JvlKW5OVRgVqm50xbQcOROrcoWO5ha0BKMi96WYUoopL47o0eBK7BA=="
                            }
                        ]
                    }
                ]
            },
            "blockid": "1ef8e34bd17ff733d697eaa88f699d101c2e069b114c51454e7e1ce385d90e7b",
            "difficulty": "600000000",
            "estimatedactivebs": "0",
            "height": 4,
            "maturitytimestamp": 0,
            "target": [
                0,
                0,
                0,
                7,
                40,
                132,
                246,
                16,
                46,
                189,
                245,
                53,
                61,
                107,
                55,
                34,
                71,
                197,
                45,
                55,
                227,
                55,
                228,
                229,
                100,
                15,
                15,
                218,
                4,
                95,
                124,
                217
            ],
            "totalcoins": "0",
            "minerpayoutcount": 4,
            "transactioncount": 6,
            "coininputcount": 1,
            "coinoutputcount": 3,
            "blockstakeinputcount": 4,
            "blockstakeoutputcount": 5,
            "minerfeecount": 1,
            "arbitrarydatacount": 0,
            "transactionsignaturecount": 5
        },
        {
            "minerpayoutids": [
                "ec7c03c33a1e5adac8770f7c9c963af58497a85d669e88980ac859dcb17a1c58"
            ],
            "transactions": [
                {
                    "id": "159a60d8dac40f89dd51b5cac5333d970d3aa4a76974e7976cddb14db26588bf",
                    "height": 2,
                    "parent": "3a1978f53183d8eeb5dbe52a70131f194978aaf6447eeccacdb840b3f09487ec",
                    "rawtransaction": {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "1eb5966d22a39f3659da8e76c887705e1fe6ffbe2c42d02f04560e495fb39b83",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "1eb5966d22a39f3659da8e76c887705e1fe6ffbe2c42d02f04560e495fb39b83",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "Z3vW4+xZrD5ZHJEKaVuGfKjjxSY2co+ycF8dI5FkjoCPW6y+4VaQe6nkApbw+Qu0YznHDuDEwBWdvGS/R7z8CQ=="
                            }
                        ]
                    },
                    "coininputoutputs": null,
                    "coinoutputids": null,
                    "blockstakeinputoutputs": [
                        {
                            "value": "1000000",
                            "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                        }
                    ],
                    "blockstakeoutputids": [
                        "1cf724879114b3e8c56d6ba50f6e25fc3d81bc074d455ffe4c211aaeb157de64"
                    ]
                }
            ],
            "rawblock": {
                "parentid": "a2ea5253b57690f696359e4e1ca360bdc0c762e6de3710f326e129d8ba9610cd",
                "timestamp": 1519818239,
                "pobsindexes": {
                    "BlockHeight": 1,
                    "TransactionIndex": 0,
                    "OutputIndex": 0
                },
                "minerpayouts": [
                    {
                        "value": "10000000000000000000000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "transactions": [
                    {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "1eb5966d22a39f3659da8e76c887705e1fe6ffbe2c42d02f04560e495fb39b83",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "1eb5966d22a39f3659da8e76c887705e1fe6ffbe2c42d02f04560e495fb39b83",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "Z3vW4+xZrD5ZHJEKaVuGfKjjxSY2co+ycF8dI5FkjoCPW6y+4VaQe6nkApbw+Qu0YznHDuDEwBWdvGS/R7z8CQ=="
                            }
                        ]
                    }
                ]
            },
            "blockid": "3a1978f53183d8eeb5dbe52a70131f194978aaf6447eeccacdb840b3f09487ec",
            "difficulty": "600000000",
            "estimatedactivebs": "0",
            "height": 2,
            "maturitytimestamp": 0,
            "target": [
                0,
                0,
                0,
                7,
                40,
                132,
                246,
                16,
                46,
                189,
                245,
                53,
                61,
                107,
                55,
                34,
                71,
                197,
                45,
                55,
                227,
                55,
                228,
                229,
                100,
                15,
                15,
                218,
                4,
                95,
                124,
                217
            ],
            "totalcoins": "0",
            "minerpayoutcount": 2,
            "transactioncount": 4,
            "coininputcount": 1,
            "coinoutputcount": 3,
            "blockstakeinputcount": 2,
            "blockstakeoutputcount": 3,
            "minerfeecount": 1,
            "arbitrarydatacount": 0,
            "transactionsignaturecount": 3
        },
        {
            "minerpayoutids": [
                "34f3fa16ba1ce28d242cde82b9a3b0f6a530af16ef3f489213f84c380361fee7"
            ],
            "transactions": [
                {
                    "id": "7d21943aa77432bae32c83bb039c7481e57d16ef13e6dd045c46ee24d6f8896d",
                    "height": 1,
                    "parent": "a2ea5253b57690f696359e4e1ca360bdc0c762e6de3710f326e129d8ba9610cd",
                    "rawtransaction": {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "3119c817784d6afbd4f77e25fd1ff9bfb5b3e177bc981358a12e2aea76df62cd",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "3119c817784d6afbd4f77e25fd1ff9bfb5b3e177bc981358a12e2aea76df62cd",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "Mef//jal1SZy99VQ0rnUzTCe+WbN3qcJD7FTNAnLiaCAyvMEOO6UvS25cSKFQVqZjMj305/wObRaqsA9X5wbAg=="
                            }
                        ]
                    },
                    "coininputoutputs": null,
                    "coinoutputids": null,
                    "blockstakeinputoutputs": [
                        {
                            "value": "1000000",
                            "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                        }
                    ],
                    "blockstakeoutputids": [
                        "1eb5966d22a39f3659da8e76c887705e1fe6ffbe2c42d02f04560e495fb39b83"
                    ]
                },
                {
                    "id": "d904e0bb8221dde4a22ae5fc982eca16ba457e357cd3be1e708b465d5b5e54cd",
                    "height": 1,
                    "parent": "a2ea5253b57690f696359e4e1ca360bdc0c762e6de3710f326e129d8ba9610cd",
                    "rawtransaction": {
                        "coininputs": [
                            {
                                "parentid": "822916455e3bb68ce1c1df5cef08e555b4e5ad153399942d628a0d298398a3fb",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "coinoutputs": [
                            {
                                "value": "98999999000000000000000000000000",
                                "unlockhash": "623071b2d6b4ca8e59e239d423b1694d23e8718f2d9c8d417ed84b7b0c766d39ddd91dd5491a"
                            },
                            {
                                "value": "1000000000000000000000000000000",
                                "unlockhash": "c69ac3db0015992b7cdf3f40c4fb4912f64c975784e2d50c909ee5119734d30784842a3b9899"
                            }
                        ],
                        "blockstakeinputs": null,
                        "blockstakeoutputs": null,
                        "minerfees": [
                            "1000000000000000000000000"
                        ],
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "822916455e3bb68ce1c1df5cef08e555b4e5ad153399942d628a0d298398a3fb",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "M1VRCsmCau2tmPGdhzQfmgzXqDV5R1KQyfJ63atVegj34DbU7dTvOULNJ+F3sTF7QU9nrYI/ZXiAcRUEuuSJAg=="
                            }
                        ]
                    },
                    "coininputoutputs": [
                        {
                            "value": "100000000000000000000000000000000",
                            "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                        }
                    ],
                    "coinoutputids": [
                        "b61874291288a6c08537c158394ab9303fe3e934b1004b89963643d56da42b47",
                        "3b68bfcbab48c6a8e09740a2b893c1608e5c909236ef7bd807905a2315aa7fcb"
                    ],
                    "blockstakeinputoutputs": null,
                    "blockstakeoutputids": null
                }
            ],
            "rawblock": {
                "parentid": "28b62a160206b2a91917e8abd2bb56ce3f78c9a6552cc535ae57c1a1e435d602",
                "timestamp": 1519817976,
                "pobsindexes": {
                    "BlockHeight": 0,
                    "TransactionIndex": 0,
                    "OutputIndex": 0
                },
                "minerpayouts": [
                    {
                        "value": "11000000000000000000000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "transactions": [
                    {
                        "coininputs": null,
                        "coinoutputs": null,
                        "blockstakeinputs": [
                            {
                                "parentid": "3119c817784d6afbd4f77e25fd1ff9bfb5b3e177bc981358a12e2aea76df62cd",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "1000000",
                                "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                            }
                        ],
                        "minerfees": null,
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "3119c817784d6afbd4f77e25fd1ff9bfb5b3e177bc981358a12e2aea76df62cd",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "Mef//jal1SZy99VQ0rnUzTCe+WbN3qcJD7FTNAnLiaCAyvMEOO6UvS25cSKFQVqZjMj305/wObRaqsA9X5wbAg=="
                            }
                        ]
                    },
                    {
                        "coininputs": [
                            {
                                "parentid": "822916455e3bb68ce1c1df5cef08e555b4e5ad153399942d628a0d298398a3fb",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "coinoutputs": [
                            {
                                "value": "98999999000000000000000000000000",
                                "unlockhash": "623071b2d6b4ca8e59e239d423b1694d23e8718f2d9c8d417ed84b7b0c766d39ddd91dd5491a"
                            },
                            {
                                "value": "1000000000000000000000000000000",
                                "unlockhash": "c69ac3db0015992b7cdf3f40c4fb4912f64c975784e2d50c909ee5119734d30784842a3b9899"
                            }
                        ],
                        "blockstakeinputs": null,
                        "blockstakeoutputs": null,
                        "minerfees": [
                            "1000000000000000000000000"
                        ],
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "822916455e3bb68ce1c1df5cef08e555b4e5ad153399942d628a0d298398a3fb",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "M1VRCsmCau2tmPGdhzQfmgzXqDV5R1KQyfJ63atVegj34DbU7dTvOULNJ+F3sTF7QU9nrYI/ZXiAcRUEuuSJAg=="
                            }
                        ]
                    }
                ]
            },
            "blockid": "a2ea5253b57690f696359e4e1ca360bdc0c762e6de3710f326e129d8ba9610cd",
            "difficulty": "600000000",
            "estimatedactivebs": "0",
            "height": 1,
            "maturitytimestamp": 0,
            "target": [
                0,
                0,
                0,
                7,
                40,
                132,
                246,
                16,
                46,
                189,
                245,
                53,
                61,
                107,
                55,
                34,
                71,
                197,
                45,
                55,
                227,
                55,
                228,
                229,
                100,
                15,
                15,
                218,
                4,
                95,
                124,
                217
            ],
            "totalcoins": "0",
            "minerpayoutcount": 1,
            "transactioncount": 3,
            "coininputcount": 1,
            "coinoutputcount": 3,
            "blockstakeinputcount": 1,
            "blockstakeoutputcount": 2,
            "minerfeecount": 1,
            "arbitrarydatacount": 0,
            "transactionsignaturecount": 2
        },
        {
            "minerpayoutids": [
                "d859fa8795103d0b1333c400affbde82639360657ff69dbb8e11b0bf97f56595"
            ],
            "transactions": [
                {
                    "id": "e0b56ef3fc86d1fb60e47de20863f28e9e96166a77c08a20780c262ff1d49867",
                    "height": 6,
                    "parent": "fb390cd62641368a7ee9c7d962d612d07a9bbe0b83495cf53a8a82862ffa534e",
                    "rawtransaction": {
                        "coininputs": [
                            {
                                "parentid": "b61874291288a6c08537c158394ab9303fe3e934b1004b89963643d56da42b47",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "qS0PbFQGjc8Jb9H0/2Q9vJ8cKC//VrcWh8xYlIiKkbU="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "coinoutputs": [
                            {
                                "value": "98999998000000000000000000000000",
                                "unlockhash": "8cc7b8bf1929737bdbf67771b3bb0d0fc460d37b36e13bd7341e3f815b961a4ae52720d2e69b"
                            }
                        ],
                        "blockstakeinputs": [
                            {
                                "parentid": "08ae8d80c10f173df0f69b20c5b4a686a1c8ecb1519acaca2ef00c17121cdd36",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "666667",
                                "unlockhash": "7fb80725b56939c38fc5c03aa9983be22048bfd9e110b14cf1172ff74e743a1fe3e4952e5f7e"
                            },
                            {
                                "value": "333333",
                                "unlockhash": "04eff9f8d75254d5bcf44c41fbf8f5b166c572a70a2b74b3d8eef067c60ef50d4c2077edc3ce"
                            }
                        ],
                        "minerfees": [
                            "1000000000000000000000000"
                        ],
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "b61874291288a6c08537c158394ab9303fe3e934b1004b89963643d56da42b47",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "Pvnoe4SJMYFhSsmZT6OkyhVW77JPd71Qq7C9DiC7/N88SdMK6nqTv3dcMHMVrgZGFZ4l5BJJCR667PipfTVCDg=="
                            },
                            {
                                "parentid": "08ae8d80c10f173df0f69b20c5b4a686a1c8ecb1519acaca2ef00c17121cdd36",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "k0wyPSUD4ByhBQEFcEi13BLS1P4gdpjbqUsQsLmbGxdAATXuJCO9jiQ5PBmgBNQN5ZkXCtjUEllF5APmFdvZCQ=="
                            }
                        ]
                    },
                    "coininputoutputs": [
                        {
                            "value": "98999999000000000000000000000000",
                            "unlockhash": "623071b2d6b4ca8e59e239d423b1694d23e8718f2d9c8d417ed84b7b0c766d39ddd91dd5491a"
                        }
                    ],
                    "coinoutputids": [
                        "2d1124a9ae22be9a30b2af830d47b331548ac55ec8e7e7336a7d3e5ac83e3b09"
                    ],
                    "blockstakeinputoutputs": [
                        {
                            "value": "1000000",
                            "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                        }
                    ],
                    "blockstakeoutputids": [
                        "be90e4d07a9da026bc69472bab3fbd5c76483bfd4295177d75a93c9723db8229",
                        "e11457ea1cb61cd70f7e1daab2c2a62dc861cba6c24f0cc83a786ecd14366801"
                    ]
                }
            ],
            "rawblock": {
                "parentid": "0dcd365344a9ee912509e965bc0231836324f44cf6eb43695ea7b5bccf817e35",
                "timestamp": 1519821626,
                "pobsindexes": {
                    "BlockHeight": 5,
                    "TransactionIndex": 0,
                    "OutputIndex": 0
                },
                "minerpayouts": [
                    {
                        "value": "11000000000000000000000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "transactions": [
                    {
                        "coininputs": [
                            {
                                "parentid": "b61874291288a6c08537c158394ab9303fe3e934b1004b89963643d56da42b47",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "qS0PbFQGjc8Jb9H0/2Q9vJ8cKC//VrcWh8xYlIiKkbU="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "coinoutputs": [
                            {
                                "value": "98999998000000000000000000000000",
                                "unlockhash": "8cc7b8bf1929737bdbf67771b3bb0d0fc460d37b36e13bd7341e3f815b961a4ae52720d2e69b"
                            }
                        ],
                        "blockstakeinputs": [
                            {
                                "parentid": "08ae8d80c10f173df0f69b20c5b4a686a1c8ecb1519acaca2ef00c17121cdd36",
                                "unlockconditions": {
                                    "timelock": 0,
                                    "publickeys": [
                                        {
                                            "algorithm": "ed25519",
                                            "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                        }
                                    ],
                                    "signaturesrequired": 1
                                }
                            }
                        ],
                        "blockstakeoutputs": [
                            {
                                "value": "666667",
                                "unlockhash": "7fb80725b56939c38fc5c03aa9983be22048bfd9e110b14cf1172ff74e743a1fe3e4952e5f7e"
                            },
                            {
                                "value": "333333",
                                "unlockhash": "04eff9f8d75254d5bcf44c41fbf8f5b166c572a70a2b74b3d8eef067c60ef50d4c2077edc3ce"
                            }
                        ],
                        "minerfees": [
                            "1000000000000000000000000"
                        ],
                        "arbitrarydata": null,
                        "transactionsignatures": [
                            {
                                "parentid": "b61874291288a6c08537c158394ab9303fe3e934b1004b89963643d56da42b47",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "Pvnoe4SJMYFhSsmZT6OkyhVW77JPd71Qq7C9DiC7/N88SdMK6nqTv3dcMHMVrgZGFZ4l5BJJCR667PipfTVCDg=="
                            },
                            {
                                "parentid": "08ae8d80c10f173df0f69b20c5b4a686a1c8ecb1519acaca2ef00c17121cdd36",
                                "publickeyindex": 0,
                                "timelock": 0,
                                "coveredfields": {
                                    "wholetransaction": true,
                                    "coininputs": null,
                                    "coinoutputs": null,
                                    "blockstakeinputs": null,
                                    "blockstakeoutputs": null,
                                    "minerfees": null,
                                    "arbitrarydata": null,
                                    "transactionsignatures": null
                                },
                                "signature": "k0wyPSUD4ByhBQEFcEi13BLS1P4gdpjbqUsQsLmbGxdAATXuJCO9jiQ5PBmgBNQN5ZkXCtjUEllF5APmFdvZCQ=="
                            }
                        ]
                    }
                ]
            },
            "blockid": "fb390cd62641368a7ee9c7d962d612d07a9bbe0b83495cf53a8a82862ffa534e",
            "difficulty": "600000000",
            "estimatedactivebs": "0",
            "height": 6,
            "maturitytimestamp": 0,
            "target": [
                0,
                0,
                0,
                7,
                40,
                132,
                246,
                16,
                46,
                189,
                245,
                53,
                61,
                107,
                55,
                34,
                71,
                197,
                45,
                55,
                227,
                55,
                228,
                229,
                100,
                15,
                15,
                218,
                4,
                95,
                124,
                217
            ],
            "totalcoins": "0",
            "minerpayoutcount": 6,
            "transactioncount": 8,
            "coininputcount": 2,
            "coinoutputcount": 4,
            "blockstakeinputcount": 6,
            "blockstakeoutputcount": 8,
            "minerfeecount": 2,
            "arbitrarydatacount": 0,
            "transactionsignaturecount": 8
        }
    ],
    "transaction": {
        "id": "0000000000000000000000000000000000000000000000000000000000000000",
        "height": 0,
        "parent": "0000000000000000000000000000000000000000000000000000000000000000",
        "rawtransaction": {
            "coininputs": null,
            "coinoutputs": null,
            "blockstakeinputs": null,
            "blockstakeoutputs": null,
            "minerfees": null,
            "arbitrarydata": null,
            "transactionsignatures": null
        },
        "coininputoutputs": null,
        "coinoutputids": null,
        "blockstakeinputoutputs": null,
        "blockstakeoutputids": null
    },
    "transactions": [
        {
            "id": "159a60d8dac40f89dd51b5cac5333d970d3aa4a76974e7976cddb14db26588bf",
            "height": 2,
            "parent": "3a1978f53183d8eeb5dbe52a70131f194978aaf6447eeccacdb840b3f09487ec",
            "rawtransaction": {
                "coininputs": null,
                "coinoutputs": null,
                "blockstakeinputs": [
                    {
                        "parentid": "1eb5966d22a39f3659da8e76c887705e1fe6ffbe2c42d02f04560e495fb39b83",
                        "unlockconditions": {
                            "timelock": 0,
                            "publickeys": [
                                {
                                    "algorithm": "ed25519",
                                    "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                }
                            ],
                            "signaturesrequired": 1
                        }
                    }
                ],
                "blockstakeoutputs": [
                    {
                        "value": "1000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "minerfees": null,
                "arbitrarydata": null,
                "transactionsignatures": [
                    {
                        "parentid": "1eb5966d22a39f3659da8e76c887705e1fe6ffbe2c42d02f04560e495fb39b83",
                        "publickeyindex": 0,
                        "timelock": 0,
                        "coveredfields": {
                            "wholetransaction": true,
                            "coininputs": null,
                            "coinoutputs": null,
                            "blockstakeinputs": null,
                            "blockstakeoutputs": null,
                            "minerfees": null,
                            "arbitrarydata": null,
                            "transactionsignatures": null
                        },
                        "signature": "Z3vW4+xZrD5ZHJEKaVuGfKjjxSY2co+ycF8dI5FkjoCPW6y+4VaQe6nkApbw+Qu0YznHDuDEwBWdvGS/R7z8CQ=="
                    }
                ]
            },
            "coininputoutputs": null,
            "coinoutputids": null,
            "blockstakeinputoutputs": [
                {
                    "value": "1000000",
                    "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                }
            ],
            "blockstakeoutputids": [
                "1cf724879114b3e8c56d6ba50f6e25fc3d81bc074d455ffe4c211aaeb157de64"
            ]
        },
        {
            "id": "5dd9e90750dc9ded436f1ac298ca3920c7ba89f60a74daf5a5dbdee73bab32be",
            "height": 4,
            "parent": "1ef8e34bd17ff733d697eaa88f699d101c2e069b114c51454e7e1ce385d90e7b",
            "rawtransaction": {
                "coininputs": null,
                "coinoutputs": null,
                "blockstakeinputs": [
                    {
                        "parentid": "7647d2ec842866fd71ade5f12be947f358744d048f2570d5ca232043c5dbe248",
                        "unlockconditions": {
                            "timelock": 0,
                            "publickeys": [
                                {
                                    "algorithm": "ed25519",
                                    "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                }
                            ],
                            "signaturesrequired": 1
                        }
                    }
                ],
                "blockstakeoutputs": [
                    {
                        "value": "1000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "minerfees": null,
                "arbitrarydata": null,
                "transactionsignatures": [
                    {
                        "parentid": "7647d2ec842866fd71ade5f12be947f358744d048f2570d5ca232043c5dbe248",
                        "publickeyindex": 0,
                        "timelock": 0,
                        "coveredfields": {
                            "wholetransaction": true,
                            "coininputs": null,
                            "coinoutputs": null,
                            "blockstakeinputs": null,
                            "blockstakeoutputs": null,
                            "minerfees": null,
                            "arbitrarydata": null,
                            "transactionsignatures": null
                        },
                        "signature": "lsfJ54PP23kf7WDJiEzziC0q83qnzt34JvlKW5OVRgVqm50xbQcOROrcoWO5ha0BKMi96WYUoopL47o0eBK7BA=="
                    }
                ]
            },
            "coininputoutputs": null,
            "coinoutputids": null,
            "blockstakeinputoutputs": [
                {
                    "value": "1000000",
                    "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                }
            ],
            "blockstakeoutputids": [
                "ee3a4e9b504d79843dd6b95a7ad3935c1d9ed1eb4c77d4f1e41681d68754174c"
            ]
        },
        {
            "id": "7d21943aa77432bae32c83bb039c7481e57d16ef13e6dd045c46ee24d6f8896d",
            "height": 1,
            "parent": "a2ea5253b57690f696359e4e1ca360bdc0c762e6de3710f326e129d8ba9610cd",
            "rawtransaction": {
                "coininputs": null,
                "coinoutputs": null,
                "blockstakeinputs": [
                    {
                        "parentid": "3119c817784d6afbd4f77e25fd1ff9bfb5b3e177bc981358a12e2aea76df62cd",
                        "unlockconditions": {
                            "timelock": 0,
                            "publickeys": [
                                {
                                    "algorithm": "ed25519",
                                    "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                }
                            ],
                            "signaturesrequired": 1
                        }
                    }
                ],
                "blockstakeoutputs": [
                    {
                        "value": "1000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "minerfees": null,
                "arbitrarydata": null,
                "transactionsignatures": [
                    {
                        "parentid": "3119c817784d6afbd4f77e25fd1ff9bfb5b3e177bc981358a12e2aea76df62cd",
                        "publickeyindex": 0,
                        "timelock": 0,
                        "coveredfields": {
                            "wholetransaction": true,
                            "coininputs": null,
                            "coinoutputs": null,
                            "blockstakeinputs": null,
                            "blockstakeoutputs": null,
                            "minerfees": null,
                            "arbitrarydata": null,
                            "transactionsignatures": null
                        },
                        "signature": "Mef//jal1SZy99VQ0rnUzTCe+WbN3qcJD7FTNAnLiaCAyvMEOO6UvS25cSKFQVqZjMj305/wObRaqsA9X5wbAg=="
                    }
                ]
            },
            "coininputoutputs": null,
            "coinoutputids": null,
            "blockstakeinputoutputs": [
                {
                    "value": "1000000",
                    "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                }
            ],
            "blockstakeoutputids": [
                "1eb5966d22a39f3659da8e76c887705e1fe6ffbe2c42d02f04560e495fb39b83"
            ]
        },
        {
            "id": "92af92ead2df3a04e0a76b8e0db74592f383f4b4774453870fd6b76ded3a1e2f",
            "height": 3,
            "parent": "14c9eea4b952cdcc4ebb7a5f20a43a04353a451591c2c6abf9541469cfca72cf",
            "rawtransaction": {
                "coininputs": null,
                "coinoutputs": null,
                "blockstakeinputs": [
                    {
                        "parentid": "1cf724879114b3e8c56d6ba50f6e25fc3d81bc074d455ffe4c211aaeb157de64",
                        "unlockconditions": {
                            "timelock": 0,
                            "publickeys": [
                                {
                                    "algorithm": "ed25519",
                                    "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                }
                            ],
                            "signaturesrequired": 1
                        }
                    }
                ],
                "blockstakeoutputs": [
                    {
                        "value": "1000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "minerfees": null,
                "arbitrarydata": null,
                "transactionsignatures": [
                    {
                        "parentid": "1cf724879114b3e8c56d6ba50f6e25fc3d81bc074d455ffe4c211aaeb157de64",
                        "publickeyindex": 0,
                        "timelock": 0,
                        "coveredfields": {
                            "wholetransaction": true,
                            "coininputs": null,
                            "coinoutputs": null,
                            "blockstakeinputs": null,
                            "blockstakeoutputs": null,
                            "minerfees": null,
                            "arbitrarydata": null,
                            "transactionsignatures": null
                        },
                        "signature": "xkFxpQowb30HsPzEfhapHVBfB1Mimj1QvhzzyMYPF8uydvaFOPZprGLseliFSeW3SPOggf6+rsGv7gE1iixrAQ=="
                    }
                ]
            },
            "coininputoutputs": null,
            "coinoutputids": null,
            "blockstakeinputoutputs": [
                {
                    "value": "1000000",
                    "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                }
            ],
            "blockstakeoutputids": [
                "7647d2ec842866fd71ade5f12be947f358744d048f2570d5ca232043c5dbe248"
            ]
        },
        {
            "id": "c2e6f47ff4a089c7fb94ce55fd31b2a2df1964b70eb9fc541b7316643c07abff",
            "height": 5,
            "parent": "0dcd365344a9ee912509e965bc0231836324f44cf6eb43695ea7b5bccf817e35",
            "rawtransaction": {
                "coininputs": null,
                "coinoutputs": null,
                "blockstakeinputs": [
                    {
                        "parentid": "ee3a4e9b504d79843dd6b95a7ad3935c1d9ed1eb4c77d4f1e41681d68754174c",
                        "unlockconditions": {
                            "timelock": 0,
                            "publickeys": [
                                {
                                    "algorithm": "ed25519",
                                    "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                }
                            ],
                            "signaturesrequired": 1
                        }
                    }
                ],
                "blockstakeoutputs": [
                    {
                        "value": "1000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "minerfees": null,
                "arbitrarydata": null,
                "transactionsignatures": [
                    {
                        "parentid": "ee3a4e9b504d79843dd6b95a7ad3935c1d9ed1eb4c77d4f1e41681d68754174c",
                        "publickeyindex": 0,
                        "timelock": 0,
                        "coveredfields": {
                            "wholetransaction": true,
                            "coininputs": null,
                            "coinoutputs": null,
                            "blockstakeinputs": null,
                            "blockstakeoutputs": null,
                            "minerfees": null,
                            "arbitrarydata": null,
                            "transactionsignatures": null
                        },
                        "signature": "j3a8mMGoGDOwP/egPZC9JG/307DvUc59nIQxe1AZ1GKGxwE9g55vB0Tr56qDjY+GRnCiokOae2HHXp2HDOdkAw=="
                    }
                ]
            },
            "coininputoutputs": null,
            "coinoutputids": null,
            "blockstakeinputoutputs": [
                {
                    "value": "1000000",
                    "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                }
            ],
            "blockstakeoutputids": [
                "08ae8d80c10f173df0f69b20c5b4a686a1c8ecb1519acaca2ef00c17121cdd36"
            ]
        },
        {
            "id": "d904e0bb8221dde4a22ae5fc982eca16ba457e357cd3be1e708b465d5b5e54cd",
            "height": 1,
            "parent": "a2ea5253b57690f696359e4e1ca360bdc0c762e6de3710f326e129d8ba9610cd",
            "rawtransaction": {
                "coininputs": [
                    {
                        "parentid": "822916455e3bb68ce1c1df5cef08e555b4e5ad153399942d628a0d298398a3fb",
                        "unlockconditions": {
                            "timelock": 0,
                            "publickeys": [
                                {
                                    "algorithm": "ed25519",
                                    "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                }
                            ],
                            "signaturesrequired": 1
                        }
                    }
                ],
                "coinoutputs": [
                    {
                        "value": "98999999000000000000000000000000",
                        "unlockhash": "623071b2d6b4ca8e59e239d423b1694d23e8718f2d9c8d417ed84b7b0c766d39ddd91dd5491a"
                    },
                    {
                        "value": "1000000000000000000000000000000",
                        "unlockhash": "c69ac3db0015992b7cdf3f40c4fb4912f64c975784e2d50c909ee5119734d30784842a3b9899"
                    }
                ],
                "blockstakeinputs": null,
                "blockstakeoutputs": null,
                "minerfees": [
                    "1000000000000000000000000"
                ],
                "arbitrarydata": null,
                "transactionsignatures": [
                    {
                        "parentid": "822916455e3bb68ce1c1df5cef08e555b4e5ad153399942d628a0d298398a3fb",
                        "publickeyindex": 0,
                        "timelock": 0,
                        "coveredfields": {
                            "wholetransaction": true,
                            "coininputs": null,
                            "coinoutputs": null,
                            "blockstakeinputs": null,
                            "blockstakeoutputs": null,
                            "minerfees": null,
                            "arbitrarydata": null,
                            "transactionsignatures": null
                        },
                        "signature": "M1VRCsmCau2tmPGdhzQfmgzXqDV5R1KQyfJ63atVegj34DbU7dTvOULNJ+F3sTF7QU9nrYI/ZXiAcRUEuuSJAg=="
                    }
                ]
            },
            "coininputoutputs": [
                {
                    "value": "100000000000000000000000000000000",
                    "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                }
            ],
            "coinoutputids": [
                "b61874291288a6c08537c158394ab9303fe3e934b1004b89963643d56da42b47",
                "3b68bfcbab48c6a8e09740a2b893c1608e5c909236ef7bd807905a2315aa7fcb"
            ],
            "blockstakeinputoutputs": null,
            "blockstakeoutputids": null
        },
        {
            "id": "ddbfa928e4556feac5528b47e63b1a93041b5627a35e2f4f8d782a50d4cbd941",
            "height": 0,
            "parent": "28b62a160206b2a91917e8abd2bb56ce3f78c9a6552cc535ae57c1a1e435d602",
            "rawtransaction": {
                "coininputs": null,
                "coinoutputs": [
                    {
                        "value": "100000000000000000000000000000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "blockstakeinputs": null,
                "blockstakeoutputs": [
                    {
                        "value": "1000000",
                        "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                    }
                ],
                "minerfees": null,
                "arbitrarydata": null,
                "transactionsignatures": null
            },
            "coininputoutputs": null,
            "coinoutputids": [
                "822916455e3bb68ce1c1df5cef08e555b4e5ad153399942d628a0d298398a3fb"
            ],
            "blockstakeinputoutputs": null,
            "blockstakeoutputids": [
                "3119c817784d6afbd4f77e25fd1ff9bfb5b3e177bc981358a12e2aea76df62cd"
            ]
        },
        {
            "id": "e0b56ef3fc86d1fb60e47de20863f28e9e96166a77c08a20780c262ff1d49867",
            "height": 6,
            "parent": "fb390cd62641368a7ee9c7d962d612d07a9bbe0b83495cf53a8a82862ffa534e",
            "rawtransaction": {
                "coininputs": [
                    {
                        "parentid": "b61874291288a6c08537c158394ab9303fe3e934b1004b89963643d56da42b47",
                        "unlockconditions": {
                            "timelock": 0,
                            "publickeys": [
                                {
                                    "algorithm": "ed25519",
                                    "key": "qS0PbFQGjc8Jb9H0/2Q9vJ8cKC//VrcWh8xYlIiKkbU="
                                }
                            ],
                            "signaturesrequired": 1
                        }
                    }
                ],
                "coinoutputs": [
                    {
                        "value": "98999998000000000000000000000000",
                        "unlockhash": "8cc7b8bf1929737bdbf67771b3bb0d0fc460d37b36e13bd7341e3f815b961a4ae52720d2e69b"
                    }
                ],
                "blockstakeinputs": [
                    {
                        "parentid": "08ae8d80c10f173df0f69b20c5b4a686a1c8ecb1519acaca2ef00c17121cdd36",
                        "unlockconditions": {
                            "timelock": 0,
                            "publickeys": [
                                {
                                    "algorithm": "ed25519",
                                    "key": "vuMqLyD344Km8w7TU0NmvHvaNRqLWx05cLBgCtZvIeo="
                                }
                            ],
                            "signaturesrequired": 1
                        }
                    }
                ],
                "blockstakeoutputs": [
                    {
                        "value": "666667",
                        "unlockhash": "7fb80725b56939c38fc5c03aa9983be22048bfd9e110b14cf1172ff74e743a1fe3e4952e5f7e"
                    },
                    {
                        "value": "333333",
                        "unlockhash": "04eff9f8d75254d5bcf44c41fbf8f5b166c572a70a2b74b3d8eef067c60ef50d4c2077edc3ce"
                    }
                ],
                "minerfees": [
                    "1000000000000000000000000"
                ],
                "arbitrarydata": null,
                "transactionsignatures": [
                    {
                        "parentid": "b61874291288a6c08537c158394ab9303fe3e934b1004b89963643d56da42b47",
                        "publickeyindex": 0,
                        "timelock": 0,
                        "coveredfields": {
                            "wholetransaction": true,
                            "coininputs": null,
                            "coinoutputs": null,
                            "blockstakeinputs": null,
                            "blockstakeoutputs": null,
                            "minerfees": null,
                            "arbitrarydata": null,
                            "transactionsignatures": null
                        },
                        "signature": "Pvnoe4SJMYFhSsmZT6OkyhVW77JPd71Qq7C9DiC7/N88SdMK6nqTv3dcMHMVrgZGFZ4l5BJJCR667PipfTVCDg=="
                    },
                    {
                        "parentid": "08ae8d80c10f173df0f69b20c5b4a686a1c8ecb1519acaca2ef00c17121cdd36",
                        "publickeyindex": 0,
                        "timelock": 0,
                        "coveredfields": {
                            "wholetransaction": true,
                            "coininputs": null,
                            "coinoutputs": null,
                            "blockstakeinputs": null,
                            "blockstakeoutputs": null,
                            "minerfees": null,
                            "arbitrarydata": null,
                            "transactionsignatures": null
                        },
                        "signature": "k0wyPSUD4ByhBQEFcEi13BLS1P4gdpjbqUsQsLmbGxdAATXuJCO9jiQ5PBmgBNQN5ZkXCtjUEllF5APmFdvZCQ=="
                    }
                ]
            },
            "coininputoutputs": [
                {
                    "value": "98999999000000000000000000000000",
                    "unlockhash": "623071b2d6b4ca8e59e239d423b1694d23e8718f2d9c8d417ed84b7b0c766d39ddd91dd5491a"
                }
            ],
            "coinoutputids": [
                "2d1124a9ae22be9a30b2af830d47b331548ac55ec8e7e7336a7d3e5ac83e3b09"
            ],
            "blockstakeinputoutputs": [
                {
                    "value": "1000000",
                    "unlockhash": "02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754"
                }
            ],
            "blockstakeoutputids": [
                "be90e4d07a9da026bc69472bab3fbd5c76483bfd4295177d75a93c9723db8229",
                "e11457ea1cb61cd70f7e1daab2c2a62dc861cba6c24f0cc83a786ecd14366801"
            ]
        }
    ]
}"""
import json
expected_address_info = json.loads(str(expected_address_info))
address =  '02b1a92f2cb1b2daec2f650717452367273335263136fae0201ddedbbcfe67648572b069c754'
actual_address_info = rivine_wallet.check_address(address=address) 
# import pdb; pdb.set_trace()
assert actual_address_info == expected_address_info, "Expected address info is not the same as check_address found"


# override the keys attribute in the wallet to use our testing address
rivine_wallet._keys = {address: object}
# after overriding the keys attributes we can try to sync the wallet
rivine_wallet.sync_wallet()

expected_unspent_coins_outputs = {'099aa602c0073ea278b086712eac30f47c66b624b2f4719e08280cd7a7307857': '10000000000000000000000000',
 '34f3fa16ba1ce28d242cde82b9a3b0f6a530af16ef3f489213f84c380361fee7': '11000000000000000000000000',
 '41cda66fcc584d3b266c2c1e54756dd15a2c3c0a29bc8bf5c636177cfd615860': '10000000000000000000000000',
 '9e9e509f9d412719ceb0f17ab0a4c950c9a4b2981cd4f9949a2212ec4caa8929': '10000000000000000000000000',
 'd859fa8795103d0b1333c400affbde82639360657ff69dbb8e11b0bf97f56595': '11000000000000000000000000',
 'ec7c03c33a1e5adac8770f7c9c963af58497a85d669e88980ac859dcb17a1c58': '10000000000000000000000000'}

assert expected_unspent_coins_outputs == rivine_wallet.unspent_coins_outputs, "Unexpected unspent coins outputs"
