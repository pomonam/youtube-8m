# Copyright 2018 DeepTopology. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from tensorflow.python.ops import nn
from tensorflow import flags
import tensorflow as tf
import tensorflow.contrib.slim as slim
import math
import modules

###############################################################################
# Necessary FLAGS #############################################################
###############################################################################
FLAGS = flags.FLAGS

flags.DEFINE_integer("CGV3_cluster_size", 7200,
                     "Number of units in the Context Gate V3 cluster layer.")


###############################################################################
# Vocabulary Correlation ######################################################
###############################################################################
class PnGateModule(modules.BaseModule):
    def __init__(self, vocab_size, is_training, scope_id=None):
        """ Initialize class PnGateModule.
        :param vocab_size: int
            Size of the classes.
        :param is_training: bool
            True iff the model is being trained.
        :param scope_id: Object
        """
        self.vocab_size = vocab_size
        self.scope_id = scope_id
        self.is_training = is_training

    def forward(self, inputs, **unused_params):
        """ PN Gate for correlation learning.
        vocabularies -> P gate -> N gate -> output
        :param inputs: batch_size x vocab_size
        :return: batch_size x vocab_size
        """
        p_gating_weights = \
            tf.get_variable("p_pn_gate",
                            [self.vocab_size, self.vocab_size],
                            initializer=tf.random_normal_initializer(stddev=1 / math.sqrt(self.vocab_size)))
        n_gating_weights = \
            tf.get_variable("n_pn_gate",
                            [self.vocab_size, self.vocab_size],
                            initializer=tf.random_normal_initializer(stddev=1 / math.sqrt(self.vocab_size)))

        # batch_size x vocab_size, vocab_size x vocab_size --> batch_size x vocab_size
        p_activation = tf.matmul(inputs, p_gating_weights)
        p_activation = tf.nn.relu6(p_activation)
        p_gate = inputs + p_activation

        # batch_size x vocab_size, vocab_size x vocab_size --> batch_size x vocab_size
        n_activation = tf.matmul(p_gate, n_gating_weights)
        n_activation = -1 * n_activation
        n_activation = tf.nn.relu6(n_activation)
        n_gate = p_gate + (-1 * n_activation)

        output = tf.nn.softmax(n_gate)
        return output


class NpGateModule(modules.BaseModule):
    def __init__(self, vocab_size, is_training, scope_id=None):
        """ Initialize class NpGateModule.
        :param vocab_size: int
            Size of the classes.
        :param is_training: bool
            True iff the model is being trained.
        :param scope_id: Object
        """
        self.vocab_size = vocab_size
        self.scope_id = scope_id
        self.is_training = is_training

    def forward(self, inputs, **unused_params):
        """ PN Gate for correlation learning.
        vocabularies -> N gate -> P gate -> output
        :param inputs: batch_size x vocab_size
        :return: batch_size x vocab_size
        """
        p_gating_weights = \
            tf.get_variable("p_np_gate",
                            [self.vocab_size, self.vocab_size],
                            initializer=tf.random_normal_initializer(stddev=1 / math.sqrt(self.vocab_size)))
        n_gating_weights = \
            tf.get_variable("n_np_gate",
                            [self.vocab_size, self.vocab_size],
                            initializer=tf.random_normal_initializer(stddev=1 / math.sqrt(self.vocab_size)))

        # batch_size x vocab_size, vocab_size x vocab_size --> batch_size x vocab_size
        n_activation = tf.matmul(inputs, n_gating_weights)
        n_activation = -1 * n_activation
        n_activation = tf.nn.relu6(n_activation)
        n_gate = inputs + (-1 * n_activation)

        # batch_size x vocab_size, vocab_size x vocab_size --> batch_size x vocab_size
        p_activation = tf.matmul(n_gate, p_gating_weights)
        p_activation = tf.nn.relu6(p_activation)
        p_gate = n_gate + p_activation
        output = tf.nn.softmax(p_gate)

        return output


class PGateModule(modules.BaseModule):
    def __init__(self, vocab_size, is_training, scope_id=None):
        """ Initialize class PGateModule.
        :param vocab_size: int
            Size of the classes.
        :param is_training: bool
            True iff the model is being trained.
        :param scope_id: Object
        """
        self.vocab_size = vocab_size
        self.scope_id = scope_id
        self.is_training = is_training

    def forward(self, inputs, **unused_params):
        """ PN Gate for correlation learning.
        vocabularies -> P gate -> output
        :param inputs: batch_size x vocab_size
        :return: batch_size x vocab_size
        """
        p_gating_weights = \
            tf.get_variable("p_p_gate",
                            [self.vocab_size, self.vocab_size],
                            initializer=tf.random_normal_initializer(stddev=1 / math.sqrt(self.vocab_size)))

        # batch_size x vocab_size, vocab_size x vocab_size --> batch_size x vocab_size
        p_activation = tf.matmul(inputs, p_gating_weights)
        p_activation = tf.nn.relu6(p_activation)
        p_gate = inputs + p_activation
        output = tf.nn.softmax(p_gate)

        return output


class CorNNGateModule(modules.BaseModule):
    def __init__(self, vocab_size, is_training, batch_norm=True, scope_id=None):
        """ Initialize a class CorNNGateModule.
        :param vocab_size: int
            Size of the classes.
        :param is_training: bool
        :param batch_norm: bool
        :param scope_id: int
        """
        self.vocab_size = vocab_size
        self.is_training = is_training
        self.batch_norm = batch_norm
        self.scope_id = scope_id

    def forward(self, inputs, **unused_params):
        """ Forward function of CorNNGateModule.
        :param inputs: batch_size x vocab_size
        :return: batch_size x vocab_size
        """
        fc1_out = slim.fully_connected(
            inputs=inputs,
            num_outputs=self.vocab_size,
            activation_fn=nn.relu,
            scope="vocab_gate1_v1{}".format("" if self.scope_id is None else str(self.scope_id))
        )

        fc2_out = slim.fully_connected(
            inputs=fc1_out,
            num_outputs=self.vocab_size,
            activation_fn=nn.relu,
            scope="vocab_gate2_v1{}".format("" if self.scope_id is None else str(self.scope_id))
        )

        fc3_out = slim.fully_connected(
            inputs=fc2_out,
            num_outputs=self.vocab_size,
            activation_fn=nn.sigmoid,
            scope="vocab_gate3_v1{}".format("" if self.scope_id is None else str(self.scope_id))
        )

        return fc3_out


###############################################################################
# Attention / Context Gate for vocabularies ###################################
###############################################################################
class ContextGateV1(modules.BaseModule):
    """
    Given the weight W, calculate sigmoid(WX + b) o X. o is an element-wise
    multiplication.

    Citation: Learnable pooling with Context Gating for video classification.
    """
    def __init__(self, vocab_size, is_training, batch_norm=True, scope_id=None):
        """ Initialize a class ContextGateV1. The idea and implementation is adopted from WILLOW.
        :param vocab_size: int
            Size of the classes.
        :param is_training: bool
        :param batch_norm: bool
        :param scope_id: int
        """
        self.vocab_size = vocab_size
        self.is_training = is_training
        self.batch_norm = batch_norm
        self.scope_id = scope_id

    def forward(self, inputs, **unused_params):
        """ Forward function of ContextGateV1
        :param inputs: batch_size x vocab_size
        :return: batch_size x vocab_size
        """
        gating_weights = tf.get_variable("vocab_gate_v1{}".format("" if self.scope_id is None else str(self.scope_id)),
                                         [self.vocab_size, self.vocab_size])

        # batch_size x vocab_size, vocab_size x vocab_size --> batch_size x vocab_size
        gates = tf.matmul(inputs, gating_weights)

        if self.batch_norm:
            gates = slim.batch_norm(
                gates,
                center=True,
                scale=True,
                is_training=self.is_training,
                scope="vocab_gate_bn_v1{}".format("" if self.scope_id is None else str(self.scope_id)))

        gates = tf.sigmoid(gates)

        # batch_size x vocab_size, batch_size x vocab_size -> batch_size x vocab_size
        updated_inputs = tf.multiply(inputs, gates)

        # batch_size x vocab_size
        return updated_inputs
